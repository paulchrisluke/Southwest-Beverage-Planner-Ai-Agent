import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BeverageDataGenerator:
    # Southwest Airlines identifier
    SWA_CALLSIGN_PREFIX = 'SWA'  # Southwest Airlines flights start with SWA
    
    # Base consumption rates per passenger
    FLIGHT_DURATION_RATES = {
        'short': 0.5,  # <2 hours
        'medium': 1.0, # 2-4 hours
        'long': 1.5    # >4 hours
    }

    # Time-based modifiers
    TIME_MODIFIERS = {
        'morning': {'hot_beverages': 1.20},  # 6AM-10AM
        'evening': {'alcoholic': 1.15},      # 6PM-11PM
        'red_eye': {'all': 0.70}             # 11PM-6AM
    }

    # Route-based modifiers
    VACATION_AIRPORTS = ['KLAS', 'KMCO', 'KHNL', 'KPHX']  # Vegas, Orlando, Honolulu, Phoenix
    BUSINESS_ROUTES = [('KBWI', 'KMDW'), ('KDCA', 'KORD')]  # Example business routes

    # Aircraft capacities
    AIRCRAFT_CAPACITY = {
        # Southwest Airlines fleet types
        'B737': 143,     # Base 737 assumption if specific variant unknown
        'B737-700': 143,
        'B737-800': 175,
        'B737-MAX8': 175,
        'B738': 175,     # 737-800 code
        'B737M8': 175,   # 737 MAX 8 code
        'B737-7': 143,   # 737-700 code
        'B737-8': 175    # Another 737-800 code
    }

    # Load factor variations
    LOAD_FACTOR_BASE = 0.85  # Base load factor
    LOAD_FACTOR_MODIFIERS = {
        'weekend': 1.10,      # 10% higher on weekends
        'summer': 1.05,       # 5% higher in summer
        'vacation_route': 1.08,  # 8% higher on vacation routes
        'business_route': 0.95,  # 5% lower on business routes
        'red_eye': 0.80       # 20% lower on red-eye flights
    }

    # Beverage distribution (percentages)
    BEVERAGE_DISTRIBUTION = {
        'soft_drinks': {
            'Coca-Cola': 0.08,
            'Diet Coke': 0.07,
            'Sprite': 0.05,
            'Dr Pepper': 0.05,
            'Diet Dr Pepper': 0.05
        },
        'hot_beverages': {
            'Regular Coffee': 0.12,
            'Decaf Coffee': 0.03,
            'Hot Tea': 0.05
        },
        'water_juice': {
            'Bottled Water': 0.20,
            'Cranberry Apple Juice': 0.08,
            'Orange Juice': 0.07
        },
        'alcoholic': {
            'Miller Lite': 0.04,
            'Bud Light': 0.04,
            'White Wine': 0.03,
            'Red Wine': 0.02,
            'Premium Spirits': 0.02
        }
    }

    # Aircraft type mapping
    SOUTHWEST_FLEET = {
        # Known ICAO24 prefixes for Southwest Airlines aircraft
        # Format: prefix: (aircraft_type, description)
        'A1B': ('B737-700', '737-700 from AirTran acquisition'),
        'ABF': ('B737-700', 'Original Southwest 737-700s'),
        'AAL': ('B737-800', 'Southwest 737-800s'),
        'AE1': ('B737M8', '737 MAX 8 new deliveries'),
        'AD9': ('B737-700', 'Southwest 737-700s'),
        'AC7': ('B737-700', 'Southwest 737-700s'),
        'AB7': ('B737-700', 'Southwest 737-700s'),
        'ADF': ('B737-800', 'Southwest 737-800s'),
        'AE8': ('B737M8', '737 MAX 8'),
        'AF1': ('B737M8', '737 MAX 8'),
        'A12': ('B737-800', 'Southwest 737-800s'),
        'A13': ('B737-800', 'Southwest 737-800s'),
        'A78': ('B737-700', 'Southwest 737-700s')
    }

    def __init__(self, data_dir: str):
        """Initialize the generator with path to flight data directory."""
        self.data_dir = data_dir

    def load_flight_data(self, airport_code: str) -> List[Dict]:
        """Load flight data for a specific airport."""
        filepath = os.path.join(self.data_dir, f"{airport_code}_2024_01_flights.json")
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            return json.load(f)

    def calculate_flight_duration(self, first_seen: int, last_seen: int) -> float:
        """Calculate flight duration in hours."""
        return (last_seen - first_seen) / 3600

    def get_flight_category(self, duration: float) -> str:
        """Categorize flight based on duration."""
        if duration < 2:
            return 'short'
        elif duration < 4:
            return 'medium'
        return 'long'

    def get_time_modifiers(self, timestamp: int) -> Dict[str, float]:
        """Get time-based modifiers based on flight time."""
        hour = datetime.fromtimestamp(timestamp).hour
        
        if 6 <= hour < 10:
            return self.TIME_MODIFIERS['morning']
        elif 18 <= hour < 23:
            return self.TIME_MODIFIERS['evening']
        elif hour >= 23 or hour < 6:
            return self.TIME_MODIFIERS['red_eye']
        return {}

    def is_vacation_route(self, origin: str, destination: str) -> bool:
        """Check if route involves vacation destinations."""
        return origin in self.VACATION_AIRPORTS or destination in self.VACATION_AIRPORTS

    def is_business_route(self, origin: str, destination: str) -> bool:
        """Check if route is a typical business route."""
        return (origin, destination) in self.BUSINESS_ROUTES or (destination, origin) in self.BUSINESS_ROUTES

    def get_aircraft_type_from_icao24(self, icao24: str) -> Optional[str]:
        """Get aircraft type from ICAO24 code."""
        if not icao24:
            logging.info("No ICAO24 code provided")
            return None
            
        # Convert to uppercase for consistency
        icao24 = icao24.upper()
        
        # Try to match the first three characters against known Southwest fleet
        prefix = icao24[:3]
        if prefix in self.SOUTHWEST_FLEET:
            aircraft_type, description = self.SOUTHWEST_FLEET[prefix]
            logging.info(f"Identified aircraft {icao24} as {aircraft_type} ({description})")
            return aircraft_type
            
        logging.warning(f"Unknown aircraft type for ICAO24 {icao24}")
        return None

    def get_aircraft_capacity(self, icao24: str) -> int:
        """Get aircraft capacity based on ICAO24 code."""
        if not icao24:
            logging.info("No ICAO24 code provided, using default B737 capacity")
            return self.AIRCRAFT_CAPACITY['B737']
            
        aircraft_type = self.get_aircraft_type_from_icao24(icao24)
        if aircraft_type and aircraft_type in self.AIRCRAFT_CAPACITY:
            return self.AIRCRAFT_CAPACITY[aircraft_type]
            
        logging.warning(f"Using default B737 capacity for ICAO24 {icao24}")
        return self.AIRCRAFT_CAPACITY['B737']

    def calculate_load_factor(self, flight_data: Dict) -> float:
        """Calculate load factor based on various factors."""
        base_factor = self.LOAD_FACTOR_BASE
        modifiers = 1.0

        # Check if weekend
        flight_date = datetime.fromtimestamp(flight_data['firstSeen'])
        if flight_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            modifiers *= self.LOAD_FACTOR_MODIFIERS['weekend']

        # Check if summer
        if 6 <= flight_date.month <= 8:  # June through August
            modifiers *= self.LOAD_FACTOR_MODIFIERS['summer']

        # Check route type
        if self.is_vacation_route(flight_data['estDepartureAirport'], 
                                flight_data['estArrivalAirport']):
            modifiers *= self.LOAD_FACTOR_MODIFIERS['vacation_route']
        elif self.is_business_route(flight_data['estDepartureAirport'], 
                                  flight_data['estArrivalAirport']):
            modifiers *= self.LOAD_FACTOR_MODIFIERS['business_route']

        # Check if red-eye
        hour = flight_date.hour
        if hour >= 23 or hour < 6:
            modifiers *= self.LOAD_FACTOR_MODIFIERS['red_eye']

        return base_factor * modifiers

    def generate_consumption_data(self, flight_data: Dict) -> Dict:
        """Generate synthetic beverage consumption data for a flight."""
        duration = self.calculate_flight_duration(flight_data['firstSeen'], flight_data['lastSeen'])
        category = self.get_flight_category(duration)
        base_rate = self.FLIGHT_DURATION_RATES[category]
        
        # Apply time modifiers
        time_mods = self.get_time_modifiers(flight_data['firstSeen'])
        
        # Get aircraft type and capacity
        aircraft_type = None
        if 'icao24' in flight_data:
            aircraft_type = self.get_aircraft_type_from_icao24(flight_data['icao24'])
        
        # Calculate estimated passengers using aircraft type and dynamic load factor
        aircraft_capacity = self.get_aircraft_capacity(flight_data.get('icao24'))
        load_factor = self.calculate_load_factor(flight_data)
        estimated_passengers = int(aircraft_capacity * load_factor)
        
        # Log capacity and passenger estimates
        logging.info(f"Flight {flight_data.get('callsign', 'unknown')}: "
                    f"Aircraft Type: {aircraft_type or 'B737'}, "
                    f"Capacity: {aircraft_capacity}, "
                    f"Est. Passengers: {estimated_passengers} "
                    f"(Load Factor: {load_factor:.2%})")
        
        # Generate consumption data for each beverage type
        consumption = {}
        for category, beverages in self.BEVERAGE_DISTRIBUTION.items():
            category_modifier = 1.0
            
            # Apply time-based modifiers
            if category in time_mods:
                category_modifier *= time_mods[category]
            
            # Apply route-based modifiers
            if (category == 'alcoholic' and 
                self.is_vacation_route(flight_data['estDepartureAirport'], 
                                    flight_data['estArrivalAirport'])):
                category_modifier *= 1.25
            
            if (category == 'hot_beverages' and 
                self.is_business_route(flight_data['estDepartureAirport'], 
                                     flight_data['estArrivalAirport'])):
                category_modifier *= 1.15

            for beverage, percentage in beverages.items():
                base_consumption = estimated_passengers * base_rate * percentage * category_modifier
                # Add some random variation (±10%)
                variation = np.random.uniform(0.9, 1.1)
                consumption[beverage] = round(base_consumption * variation)

        return {
            'flight_number': flight_data['callsign'],
            'departure': flight_data['estDepartureAirport'],
            'arrival': flight_data['estArrivalAirport'],
            'timestamp': flight_data['firstSeen'],
            'duration': duration,
            'aircraft_type': aircraft_type or 'B737',
            'aircraft_icao24': flight_data.get('icao24', 'unknown'),
            'estimated_passengers': estimated_passengers,
            'load_factor': round(load_factor, 3),
            'consumption': consumption
        }

    def is_southwest_flight(self, flight_data: Dict) -> bool:
        """Check if the flight is operated by Southwest Airlines."""
        if not flight_data.get('callsign'):
            logging.warning("No callsign found in flight data")
            return False
            
        return flight_data['callsign'].startswith(self.SWA_CALLSIGN_PREFIX)

    def process_airport_data(self, airport_code: str) -> List[Dict]:
        """Process all flights for a specific airport."""
        flights = self.load_flight_data(airport_code)
        southwest_flights = []
        other_flights = 0
        
        for flight in flights:
            if self.is_southwest_flight(flight):
                southwest_flights.append(self.generate_consumption_data(flight))
            else:
                other_flights += 1
        
        logging.info(f"{airport_code}: Found {len(southwest_flights)} Southwest flights "
                    f"and filtered out {other_flights} non-Southwest flights")
        
        return southwest_flights

    def save_consumption_data(self, airport_code: str, consumption_data: List[Dict]):
        """Save generated consumption data to file."""
        output_dir = os.path.join(self.data_dir, 'consumption')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{airport_code}_consumption.json")
        with open(output_file, 'w') as f:
            json.dump(consumption_data, f, indent=2)

def main():
    """Main function to generate beverage consumption data."""
    generator = BeverageDataGenerator('data/historical')
    
    # Process each airport's data
    airports = ['KATL', 'KBWI', 'KAUS']  # Add more airports as needed
    total_southwest_flights = 0
    
    for airport in airports:
        logging.info(f"\nProcessing {airport}...")
        consumption_data = generator.process_airport_data(airport)
        if consumption_data:
            generator.save_consumption_data(airport, consumption_data)
            total_southwest_flights += len(consumption_data)
            logging.info(f"Generated consumption data for {len(consumption_data)} Southwest flights at {airport}")
        else:
            logging.warning(f"No Southwest Airlines flights found for {airport}")
    
    logging.info(f"\nTotal Southwest flights processed: {total_southwest_flights}")

if __name__ == "__main__":
    main() 