import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_processing.weather_collector import WeatherCollector
from src.models.beverage_predictor import BeveragePredictor
import logging

logging.basicConfig(level=logging.INFO)

def generate_sample_training_data(num_samples=100):
    """Generate synthetic training data."""
    np.random.seed(42)
    
    # List of airports
    airports = ['KLAS', 'KMDW', 'KATL', 'KBWI', 'KMCO']
    
    # Base consumption ratios for each beverage within its category
    beverage_ratios = {
        'soft_drinks': {
            'coca_cola': 0.35,      # Most popular
            'diet_coke': 0.25,      # Second most popular
            'sprite': 0.20,
            'dr_pepper': 0.15,
            'ginger_ale': 0.05
        },
        'hot_beverages': {
            'coffee': 0.70,         # Most popular hot beverage
            'hot_tea': 0.20,
            'hot_cocoa': 0.10       # Seasonal/less common
        },
        'water_juice': {
            'bottled_water': 0.40,  # Most requested
            'orange_juice': 0.30,
            'cranberry_apple_juice': 0.20,
            'tomato_juice': 0.10
        },
        'alcoholic': {
            'miller_lite': 0.20,      # Most popular beer
            'dos_equis': 0.15,        # Second most popular beer
            'jack_daniels': 0.15,     # Popular whiskey
            'crown_royal': 0.10,      # Premium whiskey
            'bacardi_rum': 0.10,      # Rum for mixed drinks
            'titos_vodka': 0.10,      # Premium vodka
            'baileys': 0.05,          # For coffee drinks
            'red_wine': 0.08,         # Wine options
            'white_wine': 0.07
        }
    }
    
    # Generate random data
    data = []
    base_timestamp = int(datetime(2023, 1, 1).timestamp())
    
    for _ in range(num_samples):
        # Random timestamp within 2023
        timestamp = base_timestamp + np.random.randint(0, 365*24*3600)
        origin = np.random.choice(airports)
        dest = np.random.choice([a for a in airports if a != origin])
        
        # Generate reasonable values
        flight_data = {
            'flight_number': f'SWA{np.random.randint(1000, 9999)}',
            'timestamp': timestamp,
            'duration_hours': np.random.uniform(1.5, 5.0),
            'passenger_count': np.random.randint(100, 200),
            'is_business_route': np.random.choice([0, 1], p=[0.7, 0.3]),
            'is_vacation_route': np.random.choice([0, 1], p=[0.6, 0.4]),
            'is_holiday': np.random.choice([0, 1], p=[0.9, 0.1]),
            'origin_airport': origin,
            'destination_airport': dest
        }
        
        # Generate base consumption for each category
        base_category_consumption = {
            'soft_drinks': np.random.normal(100, 20),
            'hot_beverages': np.random.normal(50, 10),
            'water_juice': np.random.normal(80, 15),
            'alcoholic': np.random.normal(30, 8)
        }
        
        # Adjust consumption based on factors
        if flight_data['is_vacation_route']:
            base_category_consumption['alcoholic'] *= 1.3
            base_category_consumption['soft_drinks'] *= 1.2
        
        if flight_data['duration_hours'] > 3:
            for category in base_category_consumption:
                base_category_consumption[category] *= 1.4
        
        # Generate consumption for specific beverages
        for category, beverages in beverage_ratios.items():
            category_total = base_category_consumption[category]
            
            for beverage, ratio in beverages.items():
                # Add some noise to the ratio (±20%)
                adjusted_ratio = ratio * np.random.uniform(0.8, 1.2)
                
                # Calculate consumption for this specific beverage
                amount = max(0, category_total * adjusted_ratio + np.random.normal(0, 2))
                flight_data[f'{beverage}_consumption'] = int(amount)
        
        data.append(flight_data)
    
    return pd.DataFrame(data)

def main():
    logging.info("Generating sample training data...")
    df = generate_sample_training_data()
    
    logging.info("Initializing beverage predictor...")
    predictor = BeveragePredictor()
    
    logging.info("Training model...")
    predictor.train(df)
    
    logging.info("Saving trained model...")
    predictor.save_model('models/beverage_predictor.joblib')
    
    logging.info("Done! The model is now ready for predictions.")

if __name__ == "__main__":
    main() 