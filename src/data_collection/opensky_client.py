"""
OpenSky Network API client for historical data collection.
"""

import logging
import time
from datetime import datetime
from typing import List, Dict, Any

from opensky_api import OpenSkyApi

from src.config.settings import (
    OPENSKY_USERNAME,
    OPENSKY_PASSWORD,
    REQUEST_COOLDOWN
)

logger = logging.getLogger(__name__)

class OpenSkyClient:
    """Client for retrieving historical flight data from OpenSky Network."""
    
    def __init__(self):
        """Initialize the OpenSky client."""
        if OPENSKY_USERNAME and OPENSKY_PASSWORD:
            self.api = OpenSkyApi(OPENSKY_USERNAME, OPENSKY_PASSWORD)
            logger.info("Using authenticated access to OpenSky Network")
        else:
            self.api = OpenSkyApi()
            logger.warning(
                "Using anonymous access to OpenSky Network with limitations:\n"
                "- 100 requests per day\n"
                "- 10 seconds between requests\n"
                "- Limited historical data access"
            )
            
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Respect rate limiting."""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < REQUEST_COOLDOWN:
            sleep_time = REQUEST_COOLDOWN - time_since_last
            logger.debug(f"Rate limiting - waiting {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_flights_in_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all flights in a time interval using the /flights/all endpoint.
        
        Args:
            start_time: Start time
            end_time: End time
            
        Returns:
            List of flight dictionaries
        """
        self._wait_for_rate_limit()
        
        try:
            # Convert datetime to Unix timestamp
            begin = int(start_time.timestamp())
            end = int(end_time.timestamp())
            
            # Get all flights in the interval
            flights = self.api.get_flights_from_interval(begin, end)
            if flights:
                # Convert FlightData objects to dictionaries
                return [
                    {
                        'icao24': flight.icao24,
                        'callsign': flight.callsign.strip() if flight.callsign else None,
                        'firstSeen': flight.firstSeen,
                        'lastSeen': flight.lastSeen,
                        'estDepartureAirport': flight.estDepartureAirport,
                        'estArrivalAirport': flight.estArrivalAirport,
                        'estDepartureAirportHorizDistance': flight.estDepartureAirportHorizDistance,
                        'estDepartureAirportVertDistance': flight.estDepartureAirportVertDistance,
                        'estArrivalAirportHorizDistance': flight.estArrivalAirportHorizDistance,
                        'estArrivalAirportVertDistance': flight.estArrivalAirportVertDistance
                    }
                    for flight in flights
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting flights: {str(e)}")
            return [] 