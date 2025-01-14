from src.data_processing.weather_collector import WeatherCollector
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def test_weather_collection():
    # Initialize the weather collector
    collector = WeatherCollector()
    
    # Test airports
    airports = ['KLAS', 'KMDW', 'KATL']
    current_time = int(datetime.now().timestamp())
    
    for airport in airports:
        logging.info(f"\nTesting weather data for {airport}:")
        try:
            weather_data = collector.get_weather_data(airport, current_time)
            logging.info(f"Temperature: {weather_data['temperature']}°F")
            logging.info(f"Humidity: {weather_data['humidity']}%")
            logging.info(f"Wind Speed: {weather_data['wind_speed']} mph")
            logging.info(f"Precipitation: {weather_data['precipitation']} mm")
            logging.info(f"Weather Condition: {weather_data['weather_condition']}")
            logging.info(f"Is Adverse Weather: {weather_data['is_adverse_weather']}")
        except Exception as e:
            logging.error(f"Error getting weather for {airport}: {str(e)}")

if __name__ == "__main__":
    test_weather_collection() 