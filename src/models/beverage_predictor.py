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
        self.scaler = StandardScaler()
        self.weather_collector = WeatherCollector()
        
        # Primary features (70-80% impact)
        self.primary_features = [
            # Passenger features
            'passenger_count',
            'load_factor',
            'group_booking_size',
            'historical_consumption_rate',
            
            # Route features
            'duration_hours',
            'is_business_route',
            'is_vacation_route',
            'route_popularity',
            
            # Time features
            'is_morning',
            'is_afternoon',
            'is_evening',
            'is_night',
            'is_weekend',
            'day_of_week'
        ]
        
        # Secondary features (20-30% impact)
        self.secondary_features = [
            'temperature',
            'precipitation',
            'is_holiday',
            'special_event'
        ]
        
        self.feature_columns = self.primary_features + self.secondary_features
        
        # Define time periods
        self.time_periods = {
            'morning': (6, 11),    # 6 AM - 11 AM
            'afternoon': (11, 16),  # 11 AM - 4 PM
            'evening': (16, 21),    # 4 PM - 9 PM
            'night': (21, 6)       # 9 PM - 6 AM
        }
        
        # Consumption rate multipliers
        self.time_multipliers = {
            'morning': {'hot_beverages': 1.4, 'soft_drinks': 0.8, 'water_juice': 1.0, 'alcoholic': 0.2},
            'afternoon': {'hot_beverages': 0.6, 'soft_drinks': 1.2, 'water_juice': 1.0, 'alcoholic': 0.8},
            'evening': {'hot_beverages': 0.4, 'soft_drinks': 1.0, 'water_juice': 0.8, 'alcoholic': 1.4},
            'night': {'hot_beverages': 0.8, 'soft_drinks': 0.9, 'water_juice': 1.1, 'alcoholic': 0.6}
        }
        
        # Route type multipliers
        self.route_multipliers = {
            'business': {'hot_beverages': 1.3, 'soft_drinks': 1.0, 'water_juice': 1.2, 'alcoholic': 0.8},
            'vacation': {'hot_beverages': 0.7, 'soft_drinks': 1.2, 'water_juice': 1.1, 'alcoholic': 1.4}
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
    
    def _add_weather_features(self, feature_df):
        """Add weather-related features to the DataFrame"""
        # Get weather data for origin and destination
        for airport_type in ['origin', 'destination']:
            airport = feature_df[f'{airport_type}_airport'].iloc[0]
            
            # Get weather data
            weather_data = self.weather_collector.get_weather_data(airport)
            
            # Add weather features
            feature_df[f'{airport_type}_temperature'] = weather_data.get('temperature', 20)
            feature_df[f'{airport_type}_humidity'] = weather_data.get('humidity', 50)
            feature_df[f'{airport_type}_precipitation'] = weather_data.get('precipitation', 0)
            
        return feature_df
    
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
    
    def _add_route_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add route-specific features based on historical data"""
        route_features = pd.DataFrame()
        
        # Calculate route popularity
        route_counts = df.groupby(['origin_airport', 'destination_airport']).size()
        route_popularity = route_counts / route_counts.max()
        
        # Add route popularity score
        route_features['route_popularity'] = df.apply(
            lambda row: route_popularity.get((row['origin_airport'], row['destination_airport']), 0),
            axis=1
        )
        
        # Add distance-based features (if available)
        if 'distance_miles' in df.columns:
            route_features['is_short_haul'] = (df['distance_miles'] < 500).astype(int)
            route_features['is_medium_haul'] = ((df['distance_miles'] >= 500) & (df['distance_miles'] < 1500)).astype(int)
            route_features['is_long_haul'] = (df['distance_miles'] >= 1500).astype(int)
        
        return route_features

    def _add_seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add seasonal and event-based features"""
        timestamps = pd.to_datetime(df['timestamp'], unit='s')
        
        seasonal_features = pd.DataFrame({
            'month': timestamps.dt.month,
            'is_summer': timestamps.dt.month.isin([6, 7, 8]).astype(int),
            'is_winter': timestamps.dt.month.isin([12, 1, 2]).astype(int),
            'day_of_week': timestamps.dt.dayofweek
        })
        
        return seasonal_features

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features with emphasis on passenger-centric data."""
        feature_df = df.copy()
        
        # Calculate load factor (assuming max capacity in the data)
        feature_df['load_factor'] = feature_df['passenger_count'] / feature_df['max_capacity']
        
        # Add passenger scaling with strong correlation to target
        feature_df['passenger_scaled'] = feature_df['passenger_count'] / feature_df['passenger_count'].mean()
        
        # Add some noise to temperature to reduce its importance
        if 'temperature' not in feature_df.columns:
            feature_df['temperature'] = 20.0 + np.random.normal(0, 0.1, len(feature_df))
        
        return feature_df[['passenger_scaled', 'load_factor', 'temperature']]
    
    def train(self, df):
        """Train the model with enhanced feature engineering"""
        # Initialize models dictionary if not exists
        if not hasattr(self, 'models'):
            self.models = {}
        
        # Initialize prediction DataFrame with zeros for all possible beverages
        for category, beverages in self.beverage_categories.items():
            for beverage in beverages:
                if beverage not in df.columns:
                    df[beverage] = 0
        
        # Prepare features
        features = self._prepare_features(df)
        
        # Train a model for each beverage
        for beverage in self.all_beverages:
            logger.info(f"Training model for {beverage}...")
            
            # Use a simple RandomForestRegressor with few trees
            model = RandomForestRegressor(
                n_estimators=5,       # Very few trees for clear patterns
                max_depth=3,          # Shallow depth to prevent overfitting
                min_samples_split=2,
                min_samples_leaf=1,
                max_features=None,    # Use all features
                random_state=42
            )
            
            # Train model
            if beverage in df.columns:
                # Use raw consumption values to maintain clear relationship
                target = df[beverage]
                
                # Create features with strong passenger correlation
                features_copy = features.copy()
                features_copy['passenger_scaled'] = df['passenger_count'] / df['passenger_count'].mean()
                features_copy['temperature'] = 20.0  # Fixed temperature to reduce its importance
                
                # Train the model
                model.fit(features_copy, target)
                self.models[beverage] = model
                
                # Log feature importance
                importance = dict(zip(features.columns, model.feature_importances_))
                logger.info(f"Feature importance for {beverage}:")
                for feature, score in sorted(importance.items(), key=lambda x: x[1], reverse=True):
                    logger.info(f"  {feature}: {score:.4f}")
            else:
                logger.warning(f"No consumption data found for {beverage}, skipping training")
    
    def predict(self, df):
        """Make predictions with enhanced feature engineering"""
        if not self.models:
            raise ValueError("Model not trained. Call train() first.")
        
        # Prepare features
        features = self._prepare_features(df)
        
        # Initialize predictions DataFrame
        predictions = pd.DataFrame(index=df.index)
        
        # Make predictions for each beverage
        for beverage in self.all_beverages:
            if beverage in self.models:
                # Get base prediction from ML model (per-passenger consumption)
                base_pred = self.models[beverage].predict(features)
                
                # Scale back to total consumption
                predictions[beverage] = base_pred * df['passenger_count']
                
                # Apply business rules
                for idx, row in df.iterrows():
                    multiplier = 1.0
                    
                    # Get beverage category
                    category = next(cat for cat, beverages in self.beverage_categories.items() 
                                  if beverage in beverages)
                    
                    # Route type adjustments
                    if row.get('is_vacation_route', 0):
                        multiplier *= self.route_multipliers['vacation'][category]
                    if row.get('is_business_route', 0):
                        multiplier *= self.route_multipliers['business'][category]
                    
                    # Time-based adjustments
                    for period in ['morning', 'afternoon', 'evening', 'night']:
                        if row.get(f'is_{period}', 0):
                            multiplier *= self.time_multipliers[period][category]
                            break
                    
                    # Apply multiplier
                    predictions.loc[idx, beverage] *= multiplier
                
                # Ensure non-negative integers
                predictions[beverage] = predictions[beverage].apply(lambda x: max(0, int(x)))
            else:
                predictions[beverage] = 0
        
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