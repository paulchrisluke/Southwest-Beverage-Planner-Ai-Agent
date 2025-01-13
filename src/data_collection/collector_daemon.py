"""
Historical flight data collection for research purposes.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from src.config.settings import SWA_HUBS, REQUEST_COOLDOWN

from src.data_collection.flight_collector import FlightDataCollector

logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    """Collects historical flight data for research analysis."""
    
    def __init__(self):
        """Initialize the collector."""
        self.collector = FlightDataCollector()
        self.data_dir = Path("data/historical")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_progress_file(self, airport: str, year: int, month: Optional[int] = None) -> Path:
        """Get path to progress tracking file for an airport."""
        if month:
            return self.data_dir / f"{airport}_{year}_{month:02d}_progress.json"
        return self.data_dir / f"{airport}_{year}_progress.json"
        
    def _get_data_file(self, airport: str, year: int, month: Optional[int] = None) -> Path:
        """Get path to data file for an airport."""
        if month:
            return self.data_dir / f"{airport}_{year}_{month:02d}_flights.json"
        return self.data_dir / f"{airport}_{year}_flights.json"
        
    def _load_progress(self, progress_file: Path) -> List[Dict]:
        """Load collection progress from file."""
        if progress_file.exists():
            with open(progress_file) as f:
                return json.load(f)
        return []
        
    def _save_progress(self, progress_file: Path, collected_chunks: List[Dict]):
        """Save collection progress to file."""
        with open(progress_file, 'w') as f:
            json.dump(collected_chunks, f, indent=2)
            
    def _load_flights(self, data_file: Path) -> List[Dict]:
        """Load collected flights from file."""
        if data_file.exists():
            with open(data_file) as f:
                return json.load(f)
        return []
        
    def _save_flights(self, data_file: Path, flights: List[Dict]):
        """Save collected flights to file."""
        with open(data_file, 'w') as f:
            json.dump(flights, f, indent=2)
        
    def collect_airport_history(
        self,
        airport: str,
        start_date: datetime,
        end_date: datetime,
        year: int,
        month: Optional[int] = None
    ) -> List[Dict]:
        """
        Collect historical flight data for an airport.
        
        Args:
            airport: ICAO airport code
            start_date: Start date
            end_date: End date
            year: Year being collected
            month: Optional month being collected
            
        Returns:
            List of flight dictionaries
        """
        logger.info(f"Collecting historical data for {airport}")
        logger.info(f"Period: {start_date:%Y-%m-%d %H:%M} to {end_date:%Y-%m-%d %H:%M}")
        
        # Load existing progress and data
        progress_file = self._get_progress_file(airport, year, month)
        data_file = self._get_data_file(airport, year, month)
        collected_chunks = self._load_progress(progress_file)
        all_flights = self._load_flights(data_file)
        
        # Process in 2-hour chunks as required by OpenSky API
        current_start = start_date
        while current_start < end_date:
            current_end = min(current_start + timedelta(hours=2), end_date)
            
            # Check if chunk has already been collected
            chunk_info = {
                'start': current_start.isoformat(),
                'end': current_end.isoformat()
            }
            if chunk_info in collected_chunks:
                logger.info(f"Skipping already collected chunk: {current_start:%Y-%m-%d %H:%M} to {current_end:%Y-%m-%d %H:%M}")
                current_start = current_end
                continue
            
            logger.info(f"Collecting chunk: {current_start:%Y-%m-%d %H:%M} to {current_end:%Y-%m-%d %H:%M}")
            
            # Get flights for this chunk
            flights = self.collector.get_airport_flights(airport, current_start, current_end)
            all_flights.extend(flights)
            
            # Save progress and data
            collected_chunks.append(chunk_info)
            self._save_progress(progress_file, collected_chunks)
            self._save_flights(data_file, all_flights)
            
            logger.info(f"Found {len(flights)} Southwest flights")
            logger.info(f"Total flights collected: {len(all_flights)}")
            
            # Move to next chunk
            current_start = current_end
            time.sleep(REQUEST_COOLDOWN)
            
        return all_flights
        
    def collect_2024_data(self, airport: str, month: Optional[int] = None) -> List[Dict]:
        """
        Collect flight data for 2024.
        
        Args:
            airport: ICAO airport code to collect data for
            month: Optional month number (1-12) to collect data for
            
        Returns:
            List of collected flight dictionaries
        """
        if month:
            start_date = datetime(2024, month, 1)
            if month == 12:
                end_date = datetime(2025, 1, 1)
            else:
                end_date = datetime(2024, month + 1, 1)
            logger.info(f"Collecting flight data for {start_date:%B} 2024")
        else:
            start_date = datetime(2024, 1, 1)
            end_date = datetime(2025, 1, 1)
            logger.info("Collecting flight data for 2024")
            
        logger.info(f"Period: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
        
        return self.collect_airport_history(
            airport,
            start_date,
            end_date,
            2024,
            month
        )

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Start collection
    collector = HistoricalDataCollector()
    
    # Collect data for each hub one at a time
    for airport in SWA_HUBS:
        logger.info(f"\nStarting collection for {airport} ({SWA_HUBS[airport]})")
        flights = collector.collect_2024_data(airport, month=1)  # Start with January 2024
        logger.info(f"Completed collection for {airport}: {len(flights)} total flights") 