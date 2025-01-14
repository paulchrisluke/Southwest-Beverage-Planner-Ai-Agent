import pandas as pd
import numpy as np
from src.models.beverage_predictor import BeveragePredictor
from datetime import datetime, timedelta
import logging
import os

logging.basicConfig(level=logging.INFO)

def generate_training_data(num_samples=1000):
    """Generate synthetic training data with realistic patterns"""
    base_time = datetime.now()
    flights = []
    
    # Define consumption ratios for different conditions
    consumption_ratios = {
        'business_route': {
            'soft_drinks': {'coca_cola': 0.25, 'diet_coke': 0.30, 'sprite': 0.15, 
                          'dr_pepper': 0.15, 'ginger_ale': 0.15},
            'hot_beverages': {'coffee': 0.60, 'hot_tea': 0.30, 'hot_cocoa': 0.10},
            'water_juice': {'bottled_water': 0.40, 'orange_juice': 0.25, 
                          'cranberry_apple_juice': 0.20, 'tomato_juice': 0.15},
            'alcoholic': {'miller_lite': 0.20, 'dos_equis': 0.15, 'red_wine': 0.08, 
                         'white_wine': 0.07, 'jack_daniels': 0.15, 'crown_royal': 0.10,
                         'bacardi_rum': 0.10, 'titos_vodka': 0.10, 'baileys': 0.05}
        },
        'vacation_route': {
            'soft_drinks': {'coca_cola': 0.30, 'diet_coke': 0.20, 'sprite': 0.20, 
                          'dr_pepper': 0.15, 'ginger_ale': 0.15},
            'hot_beverages': {'coffee': 0.50, 'hot_tea': 0.30, 'hot_cocoa': 0.20},
            'water_juice': {'bottled_water': 0.35, 'orange_juice': 0.30, 
                          'cranberry_apple_juice': 0.20, 'tomato_juice': 0.15},
            'alcoholic': {'miller_lite': 0.20, 'dos_equis': 0.15, 'red_wine': 0.08, 
                         'white_wine': 0.07, 'jack_daniels': 0.15, 'crown_royal': 0.10,
                         'bacardi_rum': 0.10, 'titos_vodka': 0.10, 'baileys': 0.05}
        }
    }
    
    for i in range(num_samples):
        # Generate flight characteristics
        duration = np.random.choice([1.5, 2.5, 3.5, 4.5])
        passengers = np.random.randint(100, 180)
        is_business = np.random.choice([0, 1])
        is_vacation = 0 if is_business else np.random.choice([0, 1])
        is_holiday = np.random.choice([0, 1])
        
        # Base consumption rates per passenger
        base_rate = {
            1.5: 0.5,  # Short flights
            2.5: 0.8,  # Medium-short flights
            3.5: 1.0,  # Medium-long flights
            4.5: 1.2   # Long flights
        }[duration]
        
        # Generate beverage consumption
        route_type = 'business_route' if is_business else 'vacation_route'
        ratios = consumption_ratios[route_type]
        
        flight_data = {
            'flight_number': f'SWA{1000+i}',
            'timestamp': int((base_time + timedelta(hours=i)).timestamp()),
            'duration_hours': duration,
            'passenger_count': passengers,
            'is_business_route': is_business,
            'is_vacation_route': is_vacation,
            'is_holiday': is_holiday,
            'origin_airport': 'KMDW',
            'destination_airport': 'KLAS'
        }
        
        # Calculate consumption for each beverage type
        total_drinks = base_rate * passengers
        
        # Add noise to make data more realistic
        noise_factor = np.random.uniform(0.9, 1.1)
        total_drinks *= noise_factor
        
        # Adjust for holiday
        if is_holiday:
            total_drinks *= 1.15
        
        # Calculate consumption for each beverage
        for category, beverages in ratios.items():
            category_total = total_drinks * {
                'soft_drinks': 0.40,
                'hot_beverages': 0.20,
                'water_juice': 0.25,
                'alcoholic': 0.15
            }[category]
            
            for beverage, ratio in beverages.items():
                # Add some randomness to individual beverage amounts
                amount = int(category_total * ratio * np.random.uniform(0.9, 1.1))
                flight_data[beverage] = amount
        
        flights.append(flight_data)
    
    return pd.DataFrame(flights)

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Generate training data
    logging.info("Generating training data...")
    training_data = generate_training_data(num_samples=1000)
    
    # Initialize and train the model
    logging.info("Initializing beverage predictor...")
    predictor = BeveragePredictor()
    
    logging.info("Training model...")
    predictor.train(training_data)
    
    # Save the model
    model_path = 'models/beverage_predictor.joblib'
    logging.info(f"Saving model to {model_path}")
    predictor.save_model(model_path)
    
    # Test predictions
    test_flights = pd.DataFrame({
        'flight_number': ['SWA1234', 'SWA5678', 'SWA9012'],
        'timestamp': [int(datetime.now().timestamp())] * 3,
        'duration_hours': [2.5, 3.75, 1.5],
        'passenger_count': [143, 175, 143],
        'is_business_route': [1, 0, 0],
        'is_vacation_route': [0, 1, 0],
        'is_holiday': [0, 0, 1],
        'origin_airport': ['KMDW', 'KLAS', 'KBWI'],
        'destination_airport': ['KLAS', 'KMCO', 'KATL']
    })
    
    logging.info("\nTesting predictions for sample flights:")
    predictions = predictor.predict(test_flights)
    for i, pred_str in enumerate(predictions):
        logging.info(f"\nFlight {test_flights.iloc[i]['flight_number']} predictions:")
        pred = eval(pred_str)  # Convert string to dict
        for category, beverages in pred.items():
            logging.info(f"\n{category}:")
            for beverage, amount in beverages.items():
                logging.info(f"  {beverage}: {amount}")

if __name__ == '__main__':
    main() 