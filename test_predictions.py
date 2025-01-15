import json
import os
from datetime import datetime
from src.models.predictor import BeveragePredictor

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def format_flight(flight):
    """Format OpenSky flight data into our standard format."""
    return {
        'flight_number': flight['callsign'].replace('SWA', ''),
        'departure_time': datetime.fromtimestamp(flight['firstSeen']).isoformat(),
        'origin': flight['estDepartureAirport'],
        'destination': flight['estArrivalAirport'],
        'passenger_count': 150  # Default value
    }

def main():
    # Initialize predictor
    predictor = BeveragePredictor()
    print("Initialized predictor")

    # Create _site/api directory structure
    ensure_dir("_site/api")
    ensure_dir("_site/api/flights")
    ensure_dir("_site/api/predictions")

    # Load flight data
    flight_data_path = "data/historical/KLAS_2024_01_flights.json"
    with open(flight_data_path, 'r') as f:
        flights = json.load(f)
    print(f"Loaded {len(flights)} flights from {flight_data_path}")

    # Process each flight
    dates = set()
    flights_by_date = {}
    
    for flight in flights:
        # Format flight data
        formatted_flight = format_flight(flight)
        
        # Extract date from departure_time
        departure_time = datetime.fromisoformat(formatted_flight['departure_time'])
        date_str = departure_time.strftime("%Y-%m-%d")
        dates.add(date_str)
        
        # Group flights by date
        if date_str not in flights_by_date:
            flights_by_date[date_str] = []
        flights_by_date[date_str].append(formatted_flight)
        
        # Generate and save prediction
        flight_number = formatted_flight['flight_number']
        prediction = predictor.predict(formatted_flight)
        
        prediction_path = f"_site/api/predictions/{flight_number}.json"
        with open(prediction_path, 'w') as f:
            json.dump(prediction, f, indent=2)
        print(f"Saved prediction to {prediction_path}")

    # Save dates.json
    dates = sorted(list(dates))
    with open("_site/api/dates.json", 'w') as f:
        json.dump({"dates": dates}, f, indent=2)
    print(f"Saved {len(dates)} dates to dates.json")

    # Save flights by date
    for date, date_flights in flights_by_date.items():
        flight_path = f"_site/api/flights/{date}.json"
        with open(flight_path, 'w') as f:
            json.dump({"flights": date_flights}, f, indent=2)
        print(f"Saved {len(date_flights)} flights to {flight_path}")

if __name__ == "__main__":
    main() 