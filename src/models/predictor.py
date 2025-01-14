import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional
import logging
import joblib
from datetime import datetime
import os
from pathlib import Path

from src.data_processing.weather_collector import WeatherCollector
from src.data_processing.seasonal_analyzer import SeasonalAnalyzer

class BeveragePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.weather_collector = WeatherCollector()
        self.seasonal_analyzer = SeasonalAnalyzer()
        
        # Base features
        self.base_features = [
            'duration_hours',
            'passenger_count',
            'is_business_route',
            'is_vacation_route',
            'hour_of_day',
            'is_weekend'
        ]
        
        # Weather features
        self.weather_features = [
            'temperature',
            'humidity',
            'wind_speed',
            'precipitation',
            'is_adverse_weather'
        ]
        
        # Seasonal features
        self.seasonal_features = [
            'is_winter',
            'is_summer',
            'is_holiday',
            'is_major_holiday',
            'is_peak_travel'
        ]
        
        self.feature_columns = (
            self.base_features +
            self.weather_features +
            self.seasonal_features
        )

    def _prepare_features(self, flight_data: pd.DataFrame) -> np.ndarray:
        """Prepare features for the model."""
        df = flight_data.copy()
        
        # Extract base features
        df['flight_datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df['hour_of_day'] = df['flight_datetime'].dt.hour
        df['is_weekend'] = df['flight_datetime'].dt.dayofweek >= 5
        
        # Add weather features
        weather_data = []
        for idx, row in df.iterrows():
            weather = self.weather_collector.get_weather_data(
                row['origin_airport'],
                row['timestamp']
            )
            weather_data.append(weather)
        
        weather_df = pd.DataFrame(weather_data)
        for col in self.weather_features:
            df[col] = weather_df[col]
        
        # Add seasonal features
        seasonal_data = []
        for idx, row in df.iterrows():
            analysis = self.seasonal_analyzer.analyze_date(row['timestamp'])
            seasonal_data.append({
                'is_winter': analysis['season'] == 'winter',
                'is_summer': analysis['season'] == 'summer',
                'is_holiday': analysis['is_holiday'],
                'is_major_holiday': analysis['holiday_category'] == 'major',
                'is_peak_travel': analysis['is_peak_travel'],
                'consumption_modifiers': analysis['consumption_modifiers']
            })
        
        seasonal_df = pd.DataFrame(seasonal_data)
        for col in self.seasonal_features:
            df[col] = seasonal_df[col]
        
        # Convert boolean columns to int
        bool_columns = [
            'is_weekend', 'is_business_route', 'is_vacation_route',
            'is_adverse_weather', 'is_winter', 'is_summer',
            'is_holiday', 'is_major_holiday', 'is_peak_travel'
        ]
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
        
        # Log feature importance
        self._log_feature_importance()

    def predict(self, flight_data: pd.DataFrame) -> np.ndarray:
        """Predict beverage consumption for given flights."""
        X = self._prepare_features(flight_data)
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # Apply seasonal and weather modifiers
        for i, row in flight_data.iterrows():
            analysis = self.seasonal_analyzer.analyze_date(row['timestamp'])
            modifiers = analysis['consumption_modifiers']
            
            # Apply modifiers to each beverage type
            for j, bev_type in enumerate(['soft_drinks', 'hot_beverages', 'water_juice', 'alcoholic']):
                if bev_type in modifiers:
                    predictions[i][j] *= modifiers[bev_type]
        
        return predictions

    def save_model(self, path: str):
        """Save the trained model and scaler."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'base_features': self.base_features,
            'weather_features': self.weather_features,
            'seasonal_features': self.seasonal_features
        }
        joblib.dump(model_data, path)
        logging.info(f"Model saved to {path}")

    @classmethod
    def load_model(cls, path: str) -> 'BeveragePredictor':
        """Load a trained model."""
        model_data = joblib.load(path)
        predictor = cls()
        predictor.model = model_data['model']
        predictor.scaler = model_data['scaler']
        predictor.feature_columns = model_data['feature_columns']
        predictor.base_features = model_data['base_features']
        predictor.weather_features = model_data['weather_features']
        predictor.seasonal_features = model_data['seasonal_features']
        logging.info(f"Model loaded from {path}")
        return predictor

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        importance_scores = self.model.feature_importances_
        return dict(zip(self.feature_columns, importance_scores))

    def _log_feature_importance(self):
        """Log feature importance scores for analysis."""
        importance = self.get_feature_importance()
        sorted_features = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        logging.info("Feature Importance:")
        for feature, score in sorted_features:
            logging.info(f"{feature}: {score:.4f}")

def main():
    """Example usage of the BeveragePredictor."""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize predictor
    predictor = BeveragePredictor()
    
    # Example: Load and prepare data
    # flight_data = pd.read_csv('path_to_flight_data.csv')
    # consumption_data = pd.read_csv('path_to_consumption_data.csv')
    
    # Train model
    # predictor.train(flight_data, consumption_data)
    
    # Save model
    # predictor.save_model('models/beverage_predictor.joblib')
    
    logging.info("Beverage predictor setup completed")

if __name__ == "__main__":
    main() 