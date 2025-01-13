"""
SQLAlchemy models for flight data.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flight(Base):
    """Flight information."""
    
    __tablename__ = "flights"
    
    id = Column(Integer, primary_key=True)
    callsign = Column(String, nullable=False)
    icao24 = Column(String)  # Aircraft identifier
    origin = Column(String)
    destination = Column(String)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FlightState(Base):
    """Real-time flight state information."""
    
    __tablename__ = "flight_states"
    
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    callsign = Column(String, nullable=False)
    longitude = Column(Float)
    latitude = Column(Float)
    altitude = Column(Float)
    velocity = Column(Float)
    on_ground = Column(Boolean)
    last_contact = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class BeverageInventory(Base):
    """Beverage inventory for a flight."""
    
    __tablename__ = "beverage_inventory"
    
    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    beverage_type = Column(String, nullable=False)
    initial_count = Column(Integer)
    final_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WeatherData(Base):
    """Weather data for airports."""
    
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True)
    airport_code = Column(String, nullable=False)
    temperature = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 