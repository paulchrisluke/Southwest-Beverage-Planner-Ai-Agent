"""
Historical flight data collector for OpenSky Network.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from src.data_collection.opensky_client import OpenSkyClient

logger = logging.getLogger(__name__)

class FlightDataCollector:
    """Collects historical flight data from OpenSky Network."""
    
    def __init__(self):
        """Initialize the collector."""
        self.client = OpenSkyClient()
    
    def _is_southwest_flight(self, callsign: str) -> bool:
        """Check if flight is operated by Southwest Airlines."""
        return callsign and callsign.startswith('SWA')
    
    def get_airport_flights(
        self,
        airport: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all Southwest Airlines flights for an airport in a time window.
        
        Args:
            airport: ICAO airport code
            start_time: Start time
            end_time: End time
            
        Returns:
            List of flight dictionaries
        """
        # Get all flights in time range
        all_flights = self.client.get_flights_in_time_range(start_time, end_time)
        
        # Filter for flights involving this airport
        airport_flights = [
            flight for flight in all_flights
            if (flight.get('estDepartureAirport') == airport or 
                flight.get('estArrivalAirport') == airport)
        ]
        
        # Filter for Southwest Airlines flights
        swa_flights = [
            flight for flight in airport_flights
            if self._is_southwest_flight(flight.get('callsign', ''))
        ]
        
        logger.info(f"Found {len(airport_flights)} total flights and {len(swa_flights)} Southwest flights at {airport}")
        return swa_flights 