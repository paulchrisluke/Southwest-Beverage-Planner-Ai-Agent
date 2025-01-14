import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
import joblib
import logging
from typing import Dict, List, Any
import os
from datetime import datetime

class BeveragePredictor:
    """Predicts beverage consumption for flights."""
    
    # Specific beverages by category
    BEVERAGE_TYPES = {
        'soft_drinks': [
            'coca_cola',
            'diet_coke',
            'sprite',
            'dr_pepper',
            'ginger_ale'
        ],
        'hot_beverages': [
            'coffee',
            'hot_tea',
            'hot_cocoa'
        ],
        'water_juice': [
            'bottled_water',
            'orange_juice',
            'cranberry_apple_juice',
            'tomato_juice'
        ],
        'alcoholic': [
            'miller_lite',
            'dos_equis',
            'jack_daniels',
            'crown_royal',
            'bacardi_rum',
            'titos_vodka',
            'baileys',
            'red_wine',
            'white_wine'
        ]
    }
    
    # Flatten beverage types for model training
    ALL_BEVERAGES = [bev for category in BEVERAGE_TYPES.values() for bev in category]
    
    def __init__(self):
        self.models = {}
        self.scaler = None
        self.feature_columns = [
            'duration_hours',
            'passenger_count',
            'is_business_route',
            'is_vacation_route',
            'is_holiday'
        ]
    
    def _prepare_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Prepare features for model training or prediction."""
        features = df[self.feature_columns].copy()
        
        if fit:
            # Initialize scaler during training
            self.scaler = StandardScaler()
            self.scaler.fit(features)
        
        if self.scaler is None:
            raise ValueError("Scaler not initialized. Call train() first.")
        
        features_scaled = pd.DataFrame(
            self.scaler.transform(features),
            columns=self.feature_columns,
            index=features.index
        )
        
        return features_scaled
    
    def train(self, df: pd.DataFrame):
        """Train models for each specific beverage."""
        X = self._prepare_features(df, fit=True)
        
        for beverage in self.ALL_BEVERAGES:
            target = f'{beverage}_consumption'
            if target not in df.columns:
                raise ValueError(f"Training data missing column: {target}")
            
            y = df[target]
            
            # Train model
            self.models[beverage] = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            self.models[beverage].fit(X, y)
            
            # Log feature importance
            self._log_feature_importance(beverage)
    
    def predict(self, df: pd.DataFrame) -> Dict[str, Dict[str, List[float]]]:
        """Make predictions for each specific beverage, grouped by category."""
        if not self.models or self.scaler is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X = self._prepare_features(df, fit=False)
        predictions = {category: {} for category in self.BEVERAGE_TYPES.keys()}
        
        for category, beverages in self.BEVERAGE_TYPES.items():
            for beverage in beverages:
                if beverage not in self.models:
                    raise ValueError(f"Model for {beverage} not trained")
                
                pred = self.models[beverage].predict(X)
                
                # Ensure non-negative predictions
                pred = np.maximum(0, pred)
                
                # Round to nearest integer
                pred = np.round(pred).astype(int)
                
                predictions[category][beverage] = pred
        
        return predictions
    
    def save_model(self, path: str):
        """Save trained models and scaler."""
        if not self.models or self.scaler is None:
            raise ValueError("Model not trained. Call train() first.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        model_data = {
            'models': self.models,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'timestamp': datetime.now().isoformat()
        }
        
        joblib.dump(model_data, path)
        logging.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained models and scaler."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        
        model_data = joblib.load(path)
        
        self.models = model_data['models']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        
        logging.info(f"Model loaded from {path} (saved at {model_data['timestamp']})")
    
    def _log_feature_importance(self, beverage: str):
        """Log feature importance scores for a beverage."""
        importance = self.models[beverage].feature_importances_
        features = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importance
        })
        features = features.sort_values('importance', ascending=False)
        
        logging.info(f"\nFeature importance for {beverage}:")
        for _, row in features.iterrows():
            logging.info(f"{row['feature']}: {row['importance']:.4f}") 