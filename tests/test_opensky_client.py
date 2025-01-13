"""
Tests for OpenSky Network API client.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.data_collection.opensky_client import OpenSkyClient
from opensky_api import FlightData, StateVector


@pytest.fixture
def mock_opensky_api():
    """Create a mock OpenSky API."""
    with patch('src.data_collection.opensky_client.OpenSkyApi') as mock_api:
        yield mock_api


@pytest.fixture
def client(mock_opensky_api):
    """Create an OpenSky client with mocked API."""
    return OpenSkyClient()


def create_mock_flight(callsign="WN1234"):
    """Create a mock FlightData object."""
    flight = Mock(spec=FlightData)
    flight.callsign = callsign
    flight.icao24 = "abc123"
    flight.firstSeen = int(datetime.now().timestamp())
    flight.lastSeen = int((datetime.now() + timedelta(hours=2)).timestamp())
    flight.estDepartureAirport = "KLAS"
    flight.estArrivalAirport = "KLAX"
    return flight


def create_mock_state(callsign="WN1234"):
    """Create a mock StateVector object."""
    state = Mock(spec=StateVector)
    state.callsign = callsign
    state.longitude = -115.1
    state.latitude = 36.1
    state.baro_altitude = 30000
    state.velocity = 500
    state.on_ground = False
    state.last_contact = int(datetime.now().timestamp())
    return state


def test_get_southwest_flights(client, mock_opensky_api):
    """Test retrieving Southwest flights."""
    # Setup mock response
    mock_flights = [
        create_mock_flight("WN1234"),
        create_mock_flight("AA5678"),  # Non-Southwest flight
        create_mock_flight("WN5678")
    ]
    client.api.get_flights_from_interval.return_value = mock_flights

    # Test flight retrieval
    begin = int(datetime.now().timestamp())
    end = int((datetime.now() + timedelta(hours=2)).timestamp())
    flights = client.get_southwest_flights(begin, end)

    # Verify results
    assert len(flights) == 2
    assert all(f.callsign.startswith("WN") for f in flights)
    client.api.get_flights_from_interval.assert_called_once_with(begin, end)


def test_get_airport_activity(client, mock_opensky_api):
    """Test retrieving airport activity."""
    # Setup mock responses
    mock_arrivals = [create_mock_flight("WN1234"), create_mock_flight("AA5678")]
    mock_departures = [create_mock_flight("WN5678")]
    
    client.api.get_arrivals_by_airport.return_value = mock_arrivals
    client.api.get_departures_by_airport.return_value = mock_departures

    # Test airport activity retrieval
    begin = int(datetime.now().timestamp())
    end = int((datetime.now() + timedelta(hours=2)).timestamp())
    arrivals, departures = client.get_airport_activity("KLAS", begin, end)

    # Verify results
    assert len(arrivals) == 1
    assert len(departures) == 1
    assert arrivals[0].callsign == "WN1234"
    assert departures[0].callsign == "WN5678"


def test_get_aircraft_states(client, mock_opensky_api):
    """Test retrieving aircraft states."""
    # Setup mock response
    mock_states_response = Mock()
    mock_states_response.states = [
        create_mock_state("WN1234"),
        create_mock_state("AA5678"),
        create_mock_state("WN5678")
    ]
    client.api.get_states.return_value = mock_states_response

    # Test state retrieval
    states = client.get_aircraft_states()

    # Verify results
    assert len(states) == 2
    assert all(s.callsign.startswith("WN") for s in states)


def test_rate_limiting(client):
    """Test rate limiting functionality."""
    client.requests_today = 400

    # Should raise exception when limit is reached
    with pytest.raises(Exception) as exc_info:
        client._wait_for_rate_limit()
    assert "Daily request limit reached" in str(exc_info.value)

    # Test reset functionality
    client.reset_time = datetime.now() - timedelta(seconds=1)
    client._wait_for_rate_limit()
    assert client.requests_today == 1 