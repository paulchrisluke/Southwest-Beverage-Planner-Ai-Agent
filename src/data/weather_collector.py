import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WeatherCollector:
    def __init__(self):
        """Initialize the weather collector with API configuration."""
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        self.cache_dir = "data/weather_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Common US airport coordinates (lat, lon)
        self.airport_coords = {
            'KMDW': (41.7860, -87.7524),  # Chicago Midway
            'KLAS': (36.0840, -115.1537),  # Las Vegas
            'KBWI': (39.1754, -76.6682),   # Baltimore
            'KMCO': (28.4294, -81.3089),   # Orlando
            'KATL': (33.6367, -84.4281),   # Atlanta
            # Add more airports as needed
        }
    
    def get_cached_filename(self, airport: str, date: datetime) -> str:
        """Generate cache filename for weather data."""
        return os.path.join(self.cache_dir, f"{airport}_{date.strftime('%Y%m')}.csv")
    
    def fetch_historical_weather(self, 
                               airport: str, 
                               start_date: datetime,
                               end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Fetch historical weather data for a specific airport and date range.
        
        Args:
            airport: ICAO airport code
            start_date: Start date for weather data
            end_date: End date for weather data
            
        Returns:
            DataFrame with hourly weather data or None if fetch fails
        """
        if airport not in self.airport_coords:
            logger.error(f"Airport {airport} coordinates not found")
            return None
            
        lat, lon = self.airport_coords[airport]
        
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'hourly': ['temperature_2m', 'precipitation', 'cloudcover', 'windspeed_10m'],
                'timezone': 'auto'
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(data['hourly']['time']),
                'temperature': data['hourly']['temperature_2m'],
                'precipitation': data['hourly']['precipitation'],
                'cloudcover': data['hourly']['cloudcover'],
                'windspeed': data['hourly']['windspeed_10m']
            })
            
            df['airport'] = airport
            return df
            
        except Exception as e:
            logger.error(f"Error fetching weather data for {airport}: {str(e)}")
            return None
    
    def get_weather_data(self, 
                        airport: str, 
                        timestamp: datetime) -> Dict[str, float]:
        """
        Get weather data for a specific airport and timestamp.
        Uses cached data when available.
        
        Args:
            airport: ICAO airport code
            timestamp: Datetime for weather data
            
        Returns:
            Dictionary with weather metrics
        """
        cache_file = self.get_cached_filename(airport, timestamp)
        
        try:
            # Check cache first
            if os.path.exists(cache_file):
                df = pd.read_csv(cache_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            else:
                # Fetch month of data
                start_date = timestamp.replace(day=1, hour=0, minute=0, second=0)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                df = self.fetch_historical_weather(airport, start_date, end_date)
                if df is not None:
                    df.to_csv(cache_file, index=False)
                else:
                    return {}
            
            # Find closest timestamp
            closest_row = df.iloc[(df['timestamp'] - timestamp).abs().argsort()[0]]
            
            return {
                'temperature': closest_row['temperature'],
                'precipitation': closest_row['precipitation'],
                'cloudcover': closest_row['cloudcover'],
                'windspeed': closest_row['windspeed']
            }
            
        except Exception as e:
            logger.error(f"Error getting weather data for {airport} at {timestamp}: {str(e)}")
            return {} 