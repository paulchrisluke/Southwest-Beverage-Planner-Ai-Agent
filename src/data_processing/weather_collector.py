import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class WeatherCollector:
    """Collects historical weather data for airports."""
    
    # OpenWeatherMap API endpoint
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    # Airport coordinates (lat, lon)
    AIRPORT_COORDS = {
        'KATL': (33.6407, -84.4277),  # Atlanta
        'KBWI': (39.1754, -76.6682),  # Baltimore
        'KMDW': (41.7868, -87.7522),  # Chicago Midway
        'KDFW': (32.8998, -97.0403),  # Dallas
        'KDEN': (39.8561, -104.6737), # Denver
        'KLAS': (36.0840, -115.1537), # Las Vegas
        'KLAX': (33.9416, -118.4085), # Los Angeles
        'KMCO': (28.4294, -81.3089),  # Orlando
        'KPHX': (33.4484, -112.0740)  # Phoenix
    }
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeather API key not found in environment variables")
        
        self.cache_dir = 'data/weather'
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_weather_data(self, airport_code: str, timestamp: int) -> Dict[str, Any]:
        """Get historical weather data for an airport at a specific time."""
        if airport_code not in self.AIRPORT_COORDS:
            logging.warning(f"Airport {airport_code} coordinates not found")
            return self._get_default_weather()
        
        lat, lon = self.AIRPORT_COORDS[airport_code]
        
        # Check cache first
        cached_data = self._check_cache(airport_code, timestamp)
        if cached_data:
            return cached_data
        
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'imperial'  # Use Fahrenheit for temperature
            }
            
            response = requests.get(self.BASE_URL, params=params)
            response.raise_for_status()
            
            data = response.json()
            weather_data = self._process_weather_data(data)
            
            # Cache the results
            self._cache_weather_data(airport_code, timestamp, weather_data)
            
            return weather_data
            
        except Exception as e:
            logging.error(f"Failed to fetch weather data: {str(e)}")
            return self._get_default_weather()

    def _process_weather_data(self, data: Dict) -> Dict[str, Any]:
        """Process raw weather API response into useful features."""
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'precipitation': data.get('rain', {}).get('1h', 0),
            'weather_condition': data['weather'][0]['main'],
            'is_adverse_weather': self._is_adverse_weather(data)
        }

    def _is_adverse_weather(self, data: Dict) -> bool:
        """Determine if weather conditions might affect beverage consumption."""
        condition = data['weather'][0]['main'].lower()
        temp = data['main']['temp']
        
        # Conditions that might affect consumption
        adverse_conditions = ['rain', 'snow', 'thunderstorm', 'extreme']
        
        # Temperature extremes (°F)
        is_extreme_temp = temp > 85 or temp < 32
        
        return any(cond in condition for cond in adverse_conditions) or is_extreme_temp

    def _get_default_weather(self) -> Dict[str, Any]:
        """Return default weather data when API call fails."""
        return {
            'temperature': 70,  # Moderate temperature
            'humidity': 50,     # Average humidity
            'wind_speed': 5,    # Light wind
            'precipitation': 0,  # No precipitation
            'weather_condition': 'Clear',
            'is_adverse_weather': False
        }

    def _cache_key(self, airport_code: str, timestamp: int) -> str:
        """Generate cache key for weather data."""
        date = datetime.fromtimestamp(timestamp).strftime('%Y%m%d')
        return f"{self.cache_dir}/{airport_code}_{date}.json"

    def _check_cache(self, airport_code: str, timestamp: int) -> Dict[str, Any]:
        """Check if weather data exists in cache."""
        cache_file = self._cache_key(airport_code, timestamp)
        try:
            if os.path.exists(cache_file):
                return pd.read_json(cache_file, typ='series').to_dict()
        except:
            pass
        return None

    def _cache_weather_data(self, airport_code: str, timestamp: int, data: Dict[str, Any]):
        """Cache weather data to file."""
        cache_file = self._cache_key(airport_code, timestamp)
        pd.Series(data).to_json(cache_file)

def main():
    """Example usage of WeatherCollector."""
    logging.basicConfig(level=logging.INFO)
    
    collector = WeatherCollector()
    
    # Example: Get weather for Las Vegas airport
    timestamp = int(datetime.now().timestamp())
    weather = collector.get_weather_data('KLAS', timestamp)
    
    logging.info(f"Weather data for KLAS: {weather}")

if __name__ == "__main__":
    main() 