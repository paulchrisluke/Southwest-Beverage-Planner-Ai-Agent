"""
Model implementations for beverage consumption prediction.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import json
import logging
from datetime import datetime
from src.data.weather_collector import WeatherCollector

logger = logging.getLogger(__name__)

class BeveragePredictor:
    def __init__(self):
        """Initialize the beverage predictor with separate models for each beverage type."""
        self.models = {}
        self.scaler = None
        self.weather_collector = WeatherCollector()
        
        self.feature_columns = [
            'duration_hours', 'passenger_count', 'is_business_route',
            'is_vacation_route', 'is_holiday',
            # Time features
            'is_morning', 'is_afternoon', 'is_evening', 'is_night',
            'is_weekend',
            # Weather features
            'temperature', 'precipitation', 'cloudcover', 'windspeed'
        ]
        
        # Define time periods
        self.time_periods = {
            'morning': (6, 11),    # 6 AM - 11 AM
            'afternoon': (11, 16),  # 11 AM - 4 PM
            'evening': (16, 21),    # 4 PM - 9 PM
            'night': (21, 6)       # 9 PM - 6 AM
        }
        
        # Define beverage categories and types
        self.beverage_categories = {
            'soft_drinks': ['coca_cola', 'diet_coke', 'sprite', 'dr_pepper', 'ginger_ale'],
            'hot_beverages': ['coffee', 'hot_tea', 'hot_cocoa'],
            'water_juice': ['bottled_water', 'orange_juice', 'cranberry_apple_juice', 'tomato_juice'],
            'alcoholic': ['miller_lite', 'dos_equis', 'red_wine', 'white_wine', 'jack_daniels',
                         'crown_royal', 'bacardi_rum', 'titos_vodka', 'baileys']
        }
        
        # Temperature thresholds (in Celsius)
        self.temp_thresholds = {
            'cold': 5,    # Below 5°C (41°F)
            'cool': 15,   # Below 15°C (59°F)
            'warm': 25,   # Below 25°C (77°F)
            'hot': 30     # Above 30°C (86°F)
        }
        
        # Flatten beverage list for model training
        self.all_beverages = []
        for beverages in self.beverage_categories.values():
            self.all_beverages.extend(beverages)
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features to the DataFrame."""
        # Convert timestamp to datetime
        timestamps = pd.to_datetime(df['timestamp'], unit='s')
        
        # Extract hour and day of week
        hours = timestamps.dt.hour
        is_weekend = timestamps.dt.dayofweek >= 5
        
        # Initialize time period columns
        time_features = pd.DataFrame()
        for period, (start, end) in self.time_periods.items():
            if period == 'night':
                # Night spans across midnight
                is_period = (hours >= start) | (hours < end)
            else:
                is_period = (hours >= start) & (hours < end)
            time_features[f'is_{period}'] = is_period.astype(int)
        
        time_features['is_weekend'] = is_weekend.astype(int)
        
        return pd.concat([df, time_features], axis=1)
    
    def _add_weather_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add weather features to the DataFrame."""
        weather_features = []
        
        for _, row in df.iterrows():
            # Get weather for origin airport
            origin_weather = self.weather_collector.get_weather_data(
                row['origin_airport'],
                pd.to_datetime(row['timestamp'], unit='s')
            )
            
            # Use default weather if no data is available
            if not origin_weather:
                weather_features.append({
                    'temperature': 20.0,  # Default temperature in Celsius
                    'precipitation': 0.0,
                    'cloudcover': 0.0,
                    'windspeed': 0.0
                })
            else:
                weather_features.append(origin_weather)
        
        weather_df = pd.DataFrame(weather_features)
        return pd.concat([df, weather_df], axis=1)
    
    def _get_weather_multipliers(self, weather_row) -> dict:
        """Calculate weather-based multipliers for beverage categories."""
        temp = weather_row['temperature']
        precip = weather_row['precipitation']
        
        # Start with smaller base adjustments for weather
        multipliers = {
            'hot_beverages': 1.0,
            'soft_drinks': 1.0,
            'water_juice': 1.0,
            'alcoholic': 1.0
        }
        
        # Temperature-based adjustments (reduced impact)
        if temp < self.temp_thresholds['cold']:
            # Very cold weather
            multipliers['hot_beverages'] *= 1.2  # Reduced from 1.5
            multipliers['soft_drinks'] *= 0.9    # Reduced from 0.8
            multipliers['water_juice'] *= 0.9    # Reduced from 0.8
        elif temp < self.temp_thresholds['cool']:
            # Cool weather
            multipliers['hot_beverages'] *= 1.1  # Reduced from 1.3
            multipliers['soft_drinks'] *= 0.95   # Reduced from 0.9
        elif temp > self.temp_thresholds['hot']:
            # Very hot weather
            multipliers['hot_beverages'] *= 0.8  # Reduced from 0.6
            multipliers['soft_drinks'] *= 1.2    # Reduced from 1.4
            multipliers['water_juice'] *= 1.25   # Reduced from 1.5
        elif temp > self.temp_thresholds['warm']:
            # Warm weather
            multipliers['hot_beverages'] *= 0.9  # Reduced from 0.8
            multipliers['soft_drinks'] *= 1.1    # Reduced from 1.2
            multipliers['water_juice'] *= 1.15   # Reduced from 1.3
        
        # Precipitation adjustments (reduced impact)
        if precip > 0:
            multipliers['hot_beverages'] *= 1.1  # Reduced from 1.2
        
        return multipliers
    
    def _prepare_features(self, df):
        """Prepare features for model training or prediction."""
        # Add time features
        features = self._add_time_features(df)
        
        # Add weather features
        features = self._add_weather_features(features)
        
        # Select and scale features
        features = features[self.feature_columns].copy()
        
        if self.scaler is None:
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
        else:
            features_scaled = self.scaler.transform(features)
        
        return pd.DataFrame(features_scaled, columns=self.feature_columns)
    
    def train(self, df):
        """Train the model on the provided data."""
        features = self._prepare_features(df)
        
        for beverage in self.all_beverages:
            logger.info(f"Training model for {beverage}...")
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(features, df[beverage])
            self.models[beverage] = model
            
            # Log feature importance
            importance = dict(zip(self.feature_columns, model.feature_importances_))
            logger.info(f"Feature importance for {beverage}:")
            for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                logger.info(f"  {feature}: {score:.4f}")
    
    def predict(self, df):
        """Make predictions for new flights."""
        if not self.models:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self._prepare_features(df)
        predictions = []
        
        for idx, row in df.iterrows():
            flight_predictions = {}
            
            # 1. Calculate base consumption from passenger count and duration
            base_per_passenger = 1.0  # Base drinks per passenger
            if row['duration_hours'] > 4:
                base_per_passenger = 2.0  # Long flights
            elif row['duration_hours'] > 2:
                base_per_passenger = 1.5  # Medium flights
            
            total_base = row['passenger_count'] * base_per_passenger
            
            # 2. Apply route type modifiers
            route_multiplier = 1.0
            if row['is_vacation_route']:
                route_multiplier *= 1.3  # 30% more on vacation routes
            if row['is_business_route']:
                route_multiplier *= 0.9  # 10% less on business routes
            if row['is_holiday']:
                route_multiplier *= 1.2  # 20% more on holidays
            
            total_base *= route_multiplier
            
            # 3. Get time-based distribution ratios
            time_ratios = self._get_time_based_ratios(features.iloc[idx])
            
            # 4. Get weather multipliers (now secondary effects)
            weather_multipliers = self._get_weather_multipliers(features.iloc[idx])
            
            # 5. Calculate final predictions by category
            for category, beverages in self.beverage_categories.items():
                category_predictions = {}
                
                # Get base amount for this category based on time of day
                category_base = total_base * time_ratios[category]
                
                # Apply weather modifier
                category_base *= weather_multipliers[category]
                
                # Distribute among beverages in category
                beverages_in_category = len(beverages)
                base_per_beverage = category_base / beverages_in_category
                
                for beverage in beverages:
                    # Use ML model to adjust individual beverage amounts
                    model = self.models[beverage]
                    ml_modifier = model.predict(features.iloc[[idx]])[0]
                    
                    # Combine base prediction with ML adjustment
                    final_pred = base_per_beverage * (0.7 + 0.3 * ml_modifier)  # 70% rules-based, 30% ML
                    category_predictions[beverage] = max(0, int(final_pred))
                
                flight_predictions[category] = category_predictions
            
            predictions.append(json.dumps(flight_predictions))
        
        return predictions
    
    def save_model(self, path):
        """Save the trained model and scaler."""
        model_data = {
            'models': self.models,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'beverage_categories': self.beverage_categories
        }
        joblib.dump(model_data, path)
    
    def load_model(self, path):
        """Load a trained model and scaler."""
        model_data = joblib.load(path)
        self.models = model_data['models']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.beverage_categories = model_data['beverage_categories']
        
        # Rebuild all_beverages list
        self.all_beverages = []
        for beverages in self.beverage_categories.values():
            self.all_beverages.extend(beverages)
    
    def get_feature_importance(self):
        """Get feature importance for each beverage."""
        if not self.models:
            raise ValueError("Model not trained. Call train() first.")
        
        importance_by_category = {}
        for category, beverages in self.beverage_categories.items():
            category_importance = {}
            for beverage in beverages:
                model = self.models[beverage]
                importance = dict(zip(self.feature_columns, model.feature_importances_))
                category_importance[beverage] = importance
            importance_by_category[category] = category_importance
        
        return importance_by_category 
    
    def _get_time_based_ratios(self, feature_row) -> dict:
        """Calculate time-based ratios for each beverage category."""
        ratios = {
            'hot_beverages': 0.0,
            'soft_drinks': 0.0,
            'water_juice': 0.0,
            'alcoholic': 0.0
        }
        
        # Morning distribution (6-11 AM)
        if feature_row['is_morning']:
            ratios.update({
                'hot_beverages': 0.40,  # 40% hot beverages
                'soft_drinks': 0.25,    # 25% soft drinks
                'water_juice': 0.30,    # 30% water/juice
                'alcoholic': 0.05       # 5% alcoholic
            })
        
        # Afternoon distribution (11 AM-4 PM)
        elif feature_row['is_afternoon']:
            ratios.update({
                'hot_beverages': 0.15,  # 15% hot beverages
                'soft_drinks': 0.40,    # 40% soft drinks
                'water_juice': 0.30,    # 30% water/juice
                'alcoholic': 0.15       # 15% alcoholic
            })
        
        # Evening distribution (4 PM-9 PM)
        elif feature_row['is_evening']:
            ratios.update({
                'hot_beverages': 0.10,  # 10% hot beverages
                'soft_drinks': 0.35,    # 35% soft drinks
                'water_juice': 0.25,    # 25% water/juice
                'alcoholic': 0.30       # 30% alcoholic
            })
        
        # Night distribution (9 PM-6 AM)
        else:  # is_night
            ratios.update({
                'hot_beverages': 0.20,  # 20% hot beverages
                'soft_drinks': 0.30,    # 30% soft drinks
                'water_juice': 0.35,    # 35% water/juice
                'alcoholic': 0.15       # 15% alcoholic
            })
        
        # Weekend adjustments
        if feature_row['is_weekend']:
            ratios['alcoholic'] *= 1.2  # 20% more alcohol on weekends
            # Redistribute the increase from other categories
            total_adjustment = (ratios['alcoholic'] / 1.2) * 0.2
            for category in ['hot_beverages', 'soft_drinks', 'water_juice']:
                ratios[category] *= (1 - total_adjustment/3)
        
        return ratios 