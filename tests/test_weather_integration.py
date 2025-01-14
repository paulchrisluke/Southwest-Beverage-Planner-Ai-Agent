import unittest
import pandas as pd
from datetime import datetime
import logging
import sys
import os
import numpy as np

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.weather_collector import WeatherCollector
from src.models.beverage_predictor import BeveragePredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestWeatherIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.weather_collector = WeatherCollector()
        self.predictor = BeveragePredictor()
        
        # Sample flight data for testing
        self.test_flights = pd.DataFrame({
            'flight_number': ['SWA1234', 'SWA5678'],
            'timestamp': [
                int(datetime(2024, 1, 15, 14, 30).timestamp()),  # Winter afternoon
                int(datetime(2024, 7, 15, 14, 30).timestamp())   # Summer afternoon
            ],
            'duration_hours': [2.5, 2.5],
            'passenger_count': [143, 143],
            'is_business_route': [1, 1],
            'is_vacation_route': [0, 0],
            'is_holiday': [0, 0],
            'origin_airport': ['KMDW', 'KLAS'],  # Chicago (cold) vs Las Vegas (hot)
            'destination_airport': ['KLAS', 'KMDW']
        })
    
    def test_weather_collection(self):
        """Test weather data collection for different airports."""
        test_airports = ['KMDW', 'KLAS', 'KATL']
        test_date = datetime(2024, 1, 15, 14, 30)
        
        for airport in test_airports:
            logger.info(f"\nTesting weather data for {airport}:")
            weather_data = self.weather_collector.get_weather_data(airport, test_date)
            
            # Verify weather data structure
            self.assertIsInstance(weather_data, dict)
            self.assertTrue(all(key in weather_data for key in 
                ['temperature', 'precipitation', 'cloudcover', 'windspeed']))
            
            # Log weather data
            for key, value in weather_data.items():
                logger.info(f"{key}: {value}")
    
    def test_weather_based_predictions(self):
        """Test that weather affects beverage predictions appropriately."""
        # Train the model with basic data
        training_data = self._generate_training_data()
        self.predictor.train(training_data)
        
        # Create test cases for extreme weather conditions
        cold_flight = pd.DataFrame([{
            'flight_number': 'SWA9999',
            'timestamp': int(datetime(2024, 1, 15, 14, 30).timestamp()),
            'duration_hours': 2.5,
            'passenger_count': 100,
            'is_business_route': 0,
            'is_vacation_route': 0,
            'is_holiday': 0,
            'origin_airport': 'KMDW',  # Chicago in winter
            'destination_airport': 'KATL'
        }])
        
        hot_flight = pd.DataFrame([{
            'flight_number': 'SWA9998',
            'timestamp': int(datetime(2024, 7, 15, 14, 30).timestamp()),
            'duration_hours': 2.5,
            'passenger_count': 100,
            'is_business_route': 0,
            'is_vacation_route': 0,
            'is_holiday': 0,
            'origin_airport': 'KLAS',  # Las Vegas in summer
            'destination_airport': 'KATL'
        }])
        
        # Get predictions
        cold_predictions = eval(self.predictor.predict(cold_flight)[0])
        hot_predictions = eval(self.predictor.predict(hot_flight)[0])
        
        # Log predictions
        logger.info("\nPredictions for cold weather flight (Chicago):")
        self._log_predictions(cold_predictions)
        
        logger.info("\nPredictions for hot weather flight (Las Vegas):")
        self._log_predictions(hot_predictions)
        
        # Test weather effects
        self.assertGreater(
            sum(cold_predictions['hot_beverages'].values()),
            sum(hot_predictions['hot_beverages'].values()),
            "Hot beverage consumption should be higher in cold weather"
        )
        
        self.assertGreater(
            sum(hot_predictions['soft_drinks'].values()) + sum(hot_predictions['water_juice'].values()),
            sum(cold_predictions['soft_drinks'].values()) + sum(cold_predictions['water_juice'].values()),
            "Cold beverage consumption should be higher in hot weather"
        )
    
    def _generate_training_data(self):
        """Generate synthetic training data for testing weather effects only."""
        flights = []
        for month in [1, 7]:  # Winter and summer
            for hour in [8, 14, 20]:  # Morning, afternoon, evening
                for airport in ['KMDW', 'KLAS']:  # Cold vs Hot locations
                    flight = {
                        'flight_number': f'SWA{len(flights):04d}',
                        'timestamp': int(datetime(2024, month, 15, hour).timestamp()),
                        'duration_hours': 2.5,
                        'passenger_count': 100,  # Fixed passenger count for testing
                        'is_business_route': 0,
                        'is_vacation_route': 0,
                        'is_holiday': 0,
                        'origin_airport': airport,
                        'destination_airport': 'KATL'
                    }
                    
                    # Get weather data for this flight
                    weather = self.weather_collector.get_weather_data(
                        airport,
                        datetime(2024, month, 15, hour)
                    )
                    
                    # Base consumption varies by time of day and weather
                    is_morning = hour < 11
                    is_afternoon = 11 <= hour < 16
                    is_evening = 16 <= hour < 21
                    
                    # Temperature-based adjustments
                    temp = weather.get('temperature', 20)
                    is_cold = temp < 5
                    is_hot = temp > 30
                    
                    # Set base consumption for each category
                    hot_base = 80 if is_cold else 40 if is_hot else 60
                    cold_base = 40 if is_cold else 80 if is_hot else 60
                    
                    # Adjust for time of day
                    if is_morning:
                        hot_base *= 1.5
                        cold_base *= 0.7
                    elif is_afternoon:
                        hot_base *= 0.7
                        cold_base *= 1.3
                    elif is_evening:
                        hot_base *= 0.5
                        cold_base *= 1.5
                    
                    # Add random variation (±20%)
                    for category, beverages in self.predictor.beverage_categories.items():
                        for beverage in beverages:
                            if category == 'hot_beverages':
                                base = hot_base
                            elif category in ['soft_drinks', 'water_juice']:
                                base = cold_base
                            else:  # alcoholic
                                base = 50  # Fixed base for alcoholic beverages
                            
                            # Add random variation
                            variation = np.random.uniform(0.8, 1.2)
                            flight[beverage] = int(base * variation)
                    
                    flights.append(flight)
        
        return pd.DataFrame(flights)
    
    def _log_predictions(self, predictions):
        """Helper to log predictions in a readable format."""
        for category, beverages in predictions.items():
            logger.info(f"\n{category}:")
            for beverage, amount in beverages.items():
                logger.info(f"  {beverage}: {amount}")

if __name__ == '__main__':
    unittest.main() 