"""
Database models for storing flight and beverage inventory data.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.config.settings import DATABASE_URL

# Create database engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Flight(Base):
    """Flight data collected from OpenSky Network."""
    
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True)
    callsign = Column(String, index=True)  # WN flight number
    icao24 = Column(String)  # Aircraft identifier
    
    # Flight schedule
    departure_time = Column(DateTime, index=True)
    arrival_time = Column(DateTime, index=True)
    departure_airport = Column(String, index=True)
    arrival_airport = Column(String, index=True)
    
    # Flight details
    aircraft_type = Column(String)
    duration_minutes = Column(Integer)
    
    # Collection metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    beverage_inventory = relationship("BeverageInventory", back_populates="flight")
    flight_states = relationship("FlightState", back_populates="flight")


class FlightState(Base):
    """Real-time flight state data."""
    
    __tablename__ = "flight_states"

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    
    # Position data
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    velocity = Column(Float)
    
    # Status
    on_ground = Column(Boolean)
    timestamp = Column(DateTime, index=True)
    
    # Relationship
    flight = relationship("Flight", back_populates="flight_states")


class BeverageInventory(Base):
    """Beverage inventory for a specific flight."""
    
    __tablename__ = "beverage_inventory"

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey("flights.id"))
    
    # Inventory counts
    coffee_initial = Column(Integer)
    coffee_final = Column(Integer)
    water_initial = Column(Integer)
    water_final = Column(Integer)
    soda_initial = Column(Integer)
    soda_final = Column(Integer)
    juice_initial = Column(Integer)
    juice_final = Column(Integer)
    alcohol_initial = Column(Integer)
    alcohol_final = Column(Integer)
    
    # Weight calculations
    total_weight_initial = Column(Float)  # in pounds
    total_weight_final = Column(Float)  # in pounds
    
    # Collection metadata
    recorded_at = Column(DateTime, default=datetime.utcnow)
    is_actual = Column(Boolean, default=True)  # False for synthetic data
    
    # Relationship
    flight = relationship("Flight", back_populates="beverage_inventory")


class WeatherData(Base):
    """Weather conditions at airports."""
    
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True)
    airport_code = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    
    # Weather conditions
    temperature = Column(Float)  # in Celsius
    precipitation = Column(Float)  # in mm
    wind_speed = Column(Float)  # in m/s
    wind_direction = Column(Float)  # in degrees
    
    # Collection metadata
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 