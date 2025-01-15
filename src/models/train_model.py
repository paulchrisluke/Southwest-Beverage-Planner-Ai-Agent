import pandas as pd
import numpy as np
from predictor import BeveragePredictor
import logging
import os

logging.basicConfig(level=logging.INFO)

# Create some sample training data
sample_data = pd.DataFrame({
    'timestamp': [1704120608, 1704119601, 1704118532],  # Some timestamps
    'duration_hours': [2.5, 1.5, 4.5],
    'passenger_count': [150, 120, 180],
    'is_holiday': [False, False, True],
    'is_business_route': [True, False, False],
    'is_vacation_route': [False, True, False]
})

# Create sample consumption data (beverages per flight)
consumption = np.array([250, 150, 400])  # Sample beverage counts

# Initialize and train predictor
predictor = BeveragePredictor()
predictor.train(sample_data, consumption)

# Save the trained model
model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'beverage_predictor.joblib')
os.makedirs(os.path.dirname(model_path), exist_ok=True)
predictor.save_model(model_path)
logging.info(f"Model saved to {model_path}") 