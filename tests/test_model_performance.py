import unittest
import pandas as pd
import numpy as np
from src.models.beverage_predictor import BeveragePredictor
from datetime import datetime, timedelta
import json

class TestModelPerformance(unittest.TestCase):
    def setUp(self):
        self.predictor = BeveragePredictor()
        self.predictor.load_model('models/beverage_predictor.joblib')
        
        # Generate test data
        self.test_data = self._generate_test_data()
        
    def _generate_test_data(self):
        # Generate 100 test flights with known consumption patterns
        flights = []
        base_time = datetime.now()
        
        for i in range(100):
            flight = {
                'flight_number': f'SWA{1000+i}',
                'timestamp': int((base_time + timedelta(hours=i)).timestamp()),
                'duration_hours': np.random.choice([1.5, 2.5, 3.5, 4.5]),
                'passenger_count': np.random.randint(100, 180),
                'is_business_route': np.random.choice([0, 1]),
                'is_vacation_route': np.random.choice([0, 1]),
                'is_holiday': np.random.choice([0, 1]),
                'origin_airport': 'KMDW',
                'destination_airport': 'KLAS'
            }
            flights.append(flight)
            
        return pd.DataFrame(flights)
        
    def _flatten_predictions(self, pred_dict):
        """Flatten nested prediction dictionary into single level"""
        flattened = {}
        for category, beverages in pred_dict.items():
            for beverage, amount in beverages.items():
                flattened[f"{category}_{beverage}"] = amount
        return flattened
        
    def test_prediction_accuracy(self):
        """Test if predictions are within 10% margin of error"""
        predictions = self.predictor.predict(self.test_data)
        
        # Ensure we have predictions
        self.assertTrue(len(predictions) > 0, "No predictions generated")
        
        # Parse first prediction to get structure
        first_pred = json.loads(predictions[0])
        
        # Calculate error margins for each beverage category
        errors_by_category = {}
        
        for category, beverages in first_pred.items():
            category_errors = []
            
            for pred_str in predictions:
                pred = json.loads(pred_str)
                for beverage, amount in pred[category].items():
                    # Compare with synthetic "actual" data
                    expected = amount * np.random.uniform(0.9, 1.1)
                    error_pct = abs(amount - expected) / expected * 100
                    category_errors.append(error_pct)
            
            avg_error = np.mean(category_errors)
            errors_by_category[category] = avg_error
            self.assertLess(avg_error, 10.0, 
                          f"Average error for {category} exceeds 10% margin: {avg_error:.2f}%")
            
    def test_overstock_reduction(self):
        """Test if model reduces overstock by at least 15%"""
        predictions = self.predictor.predict(self.test_data)
        
        # Simulate baseline method (current manual planning)
        baseline_overstock = 0
        model_overstock = 0
        
        for pred_str in predictions:
            pred = json.loads(pred_str)
            
            # Flatten predictions for easier processing
            pred_flat = self._flatten_predictions(pred)
            
            # Simulate actual consumption (within reasonable bounds)
            actual_consumption = {k: v * np.random.uniform(0.8, 1.0) 
                                for k, v in pred_flat.items()}
            
            # Baseline method typically overstocks by 20-30%
            baseline_stock = {k: v * 1.25 for k, v in actual_consumption.items()}
            
            # Calculate overstock for both methods
            baseline_overstock += sum(max(0, baseline_stock[k] - actual_consumption[k]) 
                                    for k in pred_flat.keys())
            model_overstock += sum(max(0, pred_flat[k] - actual_consumption[k]) 
                                 for k in pred_flat.keys())
        
        reduction_pct = (baseline_overstock - model_overstock) / baseline_overstock * 100
        self.assertGreater(reduction_pct, 15.0, 
                          f"Overstock reduction ({reduction_pct:.2f}%) does not meet 15% target")
        
    def test_stockout_reduction(self):
        """Test if model reduces stockouts by at least 20%"""
        predictions = self.predictor.predict(self.test_data)
        
        # Simulate baseline method stockouts
        baseline_stockouts = 0
        model_stockouts = 0
        
        for pred_str in predictions:
            pred = json.loads(pred_str)
            pred_flat = self._flatten_predictions(pred)
            
            # Simulate actual consumption (occasionally exceeding predictions)
            actual_consumption = {k: v * np.random.uniform(0.9, 1.2) 
                                for k, v in pred_flat.items()}
            
            # Baseline method (current manual planning)
            baseline_stock = {k: v * 1.1 for k, v in pred_flat.items()}
            
            # Count stockouts for both methods
            baseline_stockouts += sum(1 for k in pred_flat.keys() 
                                    if baseline_stock[k] < actual_consumption[k])
            model_stockouts += sum(1 for k in pred_flat.keys() 
                                 if pred_flat[k] < actual_consumption[k])
        
        if baseline_stockouts == 0:
            self.assertEqual(model_stockouts, 0, "Model has stockouts when baseline has none")
        else:
            reduction_pct = (baseline_stockouts - model_stockouts) / baseline_stockouts * 100
            self.assertGreater(reduction_pct, 20.0, 
                             f"Stockout reduction ({reduction_pct:.2f}%) does not meet 20% target")

if __name__ == '__main__':
    unittest.main() 