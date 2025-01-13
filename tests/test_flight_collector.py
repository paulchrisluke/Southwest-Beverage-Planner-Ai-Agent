"""
Tests for Flight Data Collector.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.data_collection.flight_collector import FlightDataCollector
from src.models.database import Flight, FlightState


@pytest.fixture
def mock_opensky_client():
    """Create a mock OpenSky client."""
    with patch('src.data_collection.flight_collector.OpenSkyClient') as mock_client:
        yield mock_client


@pytest.fixture
def collector(mock_opensky_client):
    """Create a FlightDataCollector with mocked client."""
    return FlightDataCollector()


def test_collect_time_window_with_db(collector, mock_opensky_client, db_session):
    """Test collecting flight data and storing in database."""
    # Setup mock response
    mock_flight = Mock()
    mock_flight.callsign = "WN1234"
    mock_flight.icao24 = "abc123"
    mock_flight.firstSeen = int(datetime.now().timestamp())
    mock_flight.lastSeen = int((datetime.now() + timedelta(hours=2)).timestamp())
    mock_flight.estDepartureAirport = "KLAS"
    mock_flight.estArrivalAirport = "KLAX"
    
    collector.client.get_southwest_flights.return_value = [mock_flight]

    # Test collection
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    flights = collector.collect_time_window(start_time, end_time)

    # Verify results in memory
    assert len(flights) == 1
    assert collector.client.get_southwest_flights.call_count == 1

    # Verify database entries
    db_flights = db_session.query(Flight).filter_by(callsign="WN1234").all()
    assert len(db_flights) == 1
    assert db_flights[0].departure_airport == "KLAS"
    assert db_flights[0].arrival_airport == "KLAX"


def test_track_active_flights_with_db(collector, mock_opensky_client, db_session):
    """Test tracking active flights and storing states in database."""
    # Create a flight in the database
    flight = Flight(
        callsign="WN1234",
        icao24="abc123",
        departure_airport="KLAS",
        arrival_airport="KLAX"
    )
    db_session.add(flight)
    db_session.commit()

    # Setup mock response
    mock_state = Mock()
    mock_state.callsign = "WN1234"
    mock_state.longitude = -115.1
    mock_state.latitude = 36.1
    mock_state.baro_altitude = 30000
    mock_state.velocity = 500
    mock_state.on_ground = False
    mock_state.last_contact = int(datetime.now().timestamp())
    
    collector.client.get_aircraft_states.return_value = [mock_state]

    # Test tracking
    states = collector.track_active_flights()

    # Verify results in memory
    assert len(states) == 1
    assert states[0]['callsign'] == "WN1234"
    assert states[0]['position'] == (-115.1, 36.1)

    # Verify database entries
    db_states = db_session.query(FlightState).filter(
        FlightState.flight_id == flight.id
    ).all()
    assert len(db_states) == 1
    assert db_states[0].latitude == 36.1
    assert db_states[0].longitude == -115.1


def test_collect_time_window_error_handling(collector, mock_opensky_client, db_session):
    """Test error handling in time window collection."""
    # Setup mock to raise exception
    collector.client.get_southwest_flights.side_effect = Exception("API Error")

    # Test collection with error
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=2)
    flights = collector.collect_time_window(start_time, end_time)

    # Verify results
    assert len(flights) == 0
    
    # Verify no database entries were created
    db_flights = db_session.query(Flight).all()
    assert len(db_flights) == 0 