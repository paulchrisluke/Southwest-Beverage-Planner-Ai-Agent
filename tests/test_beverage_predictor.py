import unittest
import pandas as pd
import json
import os
from src.models.beverage_predictor import BeveragePredictor
from unittest.mock import patch
import numpy as np

class TestBeveragePredictor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test data and predictor instance"""
        cls.predictor = BeveragePredictor()
        cls.test_data_path = 'tests/sample_data/test_consumption.csv'
        
        # Mock airport coordinates
        cls.mock_coordinates = {
            'LAS': (36.0840, -115.1537),  # Las Vegas
            'JFK': (40.6413, -73.7781)    # New York JFK
        }
        
        # Update the weather collector's airport coordinates
        cls.predictor.weather_collector.airport_coords = cls.mock_coordinates
        
        # Mock the weather data method to return default values
        def mock_weather(*args, **kwargs):
            return {
                'temperature': 20.0,
                'precipitation': 0.0,
                'cloudcover': 0.0,
                'windspeed': 5.0
            }
        
        cls.predictor.weather_collector.get_weather_data = mock_weather
        
        # Ensure test data exists
        if not os.path.exists(cls.test_data_path):
            raise FileNotFoundError(f"Test data not found at {cls.test_data_path}")
        
        # Load test data
        cls.test_df = pd.read_csv(cls.test_data_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        patch.stopall()
    
    def test_data_transformation(self):
        """Test the data transformation process"""
        from app import transform_consumption_data
        
        # Transform the test data
        transformed_df = transform_consumption_data(self.test_df)
        
        # Check basic transformations
        self.assertIn('timestamp', transformed_df.columns)
        self.assertIn('coca_cola', transformed_df.columns)
        self.assertIn('coffee', transformed_df.columns)
        
        # Verify beverage counts
        first_row = transformed_df.iloc[0]
        self.assertEqual(first_row['coca_cola'], 45)
        self.assertEqual(first_row['coffee'], 60)
    
    def test_feature_engineering(self):
        """Test feature engineering with focus on passenger-centric features"""
        # Transform data first
        from app import transform_consumption_data
        transformed_df = transform_consumption_data(self.test_df)
        
        # Add required columns for testing
        transformed_df['max_capacity'] = 175  # Typical 737 capacity
        transformed_df['passenger_count'] = 150  # Example passenger count
        
        # Test passenger-centric features
        feature_df = self.predictor._prepare_features(transformed_df)
        
        # Verify primary features exist
        self.assertIn('passenger_scaled', feature_df.columns)
        self.assertIn('load_factor', feature_df.columns)
        self.assertIn('temperature', feature_df.columns)
        
        # Test load factor calculation
        expected_load_factor = 150 / 175  # passenger_count / max_capacity
        self.assertAlmostEqual(feature_df['load_factor'].iloc[0], expected_load_factor)
        
        # Test passenger scaling calculation
        self.assertAlmostEqual(feature_df['passenger_scaled'].iloc[0], 1.0)  # Since we only have one row
    
    def test_model_training(self):
        """Test model training with passenger-centric approach"""
        # Prepare test data with passenger-centric features and multiple examples
        test_data = {
            'timestamp': [1641024000] * 10,  # 10 examples
            'flight_number': ['WN1234'] * 10,
            'origin_airport': ['LAS'] * 10,
            'destination_airport': ['JFK'] * 10,
            'passenger_count': [50, 100, 150, 120, 80, 160, 140, 90, 110, 130],  # Varying passenger counts
            'max_capacity': [175] * 10,
            'duration_hours': [5.0] * 10,
            'is_business_route': [1] * 10,
            'is_vacation_route': [0] * 10,
            'coca_cola': [20, 40, 60, 48, 32, 64, 56, 36, 44, 52],  # Roughly scales with passenger count
            'coffee': [25, 50, 75, 60, 40, 80, 70, 45, 55, 65]      # Roughly scales with passenger count
        }
        df = pd.DataFrame(test_data)
        
        # Set random seed for reproducibility
        np.random.seed(42)
        
        # Train the model
        self.predictor.train(df)
        
        # Verify models were created
        self.assertTrue(len(self.predictor.models) > 0)
        self.assertIn('coca_cola', self.predictor.models)
        self.assertIn('coffee', self.predictor.models)
        
        # Test feature importance with minimal features
        if hasattr(self.predictor.models['coca_cola'], 'feature_importances_'):
            importances = dict(zip(['passenger_scaled', 'load_factor', 'temperature'],
                                 self.predictor.models['coca_cola'].feature_importances_))
            
            # Print importances for debugging
            print("\nFeature importances:", importances)
            
            # Verify passenger scaling has higher importance than temperature
            self.assertGreater(importances['passenger_scaled'], importances['temperature'],
                             "Passenger scaling should have higher importance than temperature")
    
    def test_prediction(self):
        """Test prediction with emphasis on passenger impact"""
        # Create training data that establishes the relationship
        train_data = {
            'timestamp': [1641024000] * 5,
            'flight_number': ['WN1234'] * 5,
            'origin_airport': ['LAS'] * 5,
            'destination_airport': ['JFK'] * 5,
            'max_capacity': [175] * 5,
            'duration_hours': [5.0] * 5,
            'is_business_route': [1] * 5,
            'is_vacation_route': [0] * 5,
            'passenger_count': [50, 75, 100, 125, 150],
            'coca_cola': [20, 30, 40, 50, 60],     # Clear scaling with passenger count
            'coffee': [25, 37, 50, 62, 75]         # Clear scaling with passenger count
        }
        self.predictor.train(pd.DataFrame(train_data))
        
        # Create test data with varying passenger counts
        test_data = {
            'timestamp': [1641024000] * 3,
            'flight_number': ['WN1234'] * 3,
            'origin_airport': ['LAS'] * 3,
            'destination_airport': ['JFK'] * 3,
            'max_capacity': [175] * 3,
            'duration_hours': [5.0] * 3,
            'is_business_route': [1] * 3,
            'is_vacation_route': [0] * 3,
            'passenger_count': [50, 100, 150]  # Test different passenger counts
        }
        df = pd.DataFrame(test_data)
        
        # Make predictions
        predictions = self.predictor.predict(df)
        
        # Verify predictions scale with passenger count
        for beverage in ['coca_cola', 'coffee']:  # Test core beverages
            if beverage in predictions.columns:
                pred_values = predictions[beverage].values
                # Check that predictions increase with passenger count
                self.assertTrue(pred_values[0] < pred_values[1] < pred_values[2],
                              f"Predictions for {beverage} don't scale with passenger count")

if __name__ == '__main__':
    unittest.main() 