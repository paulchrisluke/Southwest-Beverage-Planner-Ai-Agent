import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional
import logging
import joblib
from datetime import datetime

class BeveragePredictor:
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the predictor, optionally loading a saved model."""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'duration_hours',
            'passenger_count',
            'is_weekend',
            'is_holiday',
            'is_summer',
            'hour_of_day',
            'is_business_route',
            'is_vacation_route'
        ]
        
        if model_path:
            self.load_model(model_path)

    def _prepare_features(self, flight_data: pd.DataFrame) -> np.ndarray:
        """Prepare features for the model."""
        df = flight_data.copy()
        
        # Extract time-based features
        df['flight_datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df['is_weekend'] = df['flight_datetime'].dt.dayofweek >= 5
        df['hour_of_day'] = df['flight_datetime'].dt.hour
        df['is_summer'] = df['flight_datetime'].dt.month.isin([6, 7, 8])
        
        # Convert boolean columns to int
        bool_columns = ['is_weekend', 'is_holiday', 'is_summer', 
                       'is_business_route', 'is_vacation_route']
        for col in bool_columns:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        # Ensure all feature columns exist
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        return df[self.feature_columns].values

    def train(self, flight_data: pd.DataFrame, consumption_data: pd.DataFrame):
        """Train the model on historical data."""
        X = self._prepare_features(flight_data)
        y = consumption_data.values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        logging.info("Model training completed")

    def predict(self, flight_data: pd.DataFrame) -> np.ndarray:
        """Predict beverage consumption for given flights."""
        X = self._prepare_features(flight_data)
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def save_model(self, path: str):
        """Save the trained model and scaler."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, path)
        logging.info(f"Model saved to {path}")

    def load_model(self, path: str) -> 'BeveragePredictor':
        """Load a trained model."""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            logging.info(f"Model loaded from {path}")
            return self
        except Exception as e:
            logging.error(f"Error loading model from {path}: {str(e)}")
            raise

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_columns, importance_scores))

def main():
    """Example usage of the BeveragePredictor."""
    logging.basicConfig(level=logging.INFO)
    
    # Load your data here
    # flight_data = pd.read_csv('path_to_flight_data.csv')
    # consumption_data = pd.read_csv('path_to_consumption_data.csv')
    
    # Initialize and train predictor
    predictor = BeveragePredictor()
    # predictor.train(flight_data, consumption_data)
    
    # Save model
    # predictor.save_model('models/beverage_predictor.joblib')
    
    logging.info("Beverage predictor setup completed")

if __name__ == "__main__":
    main() 