"""
Configuration settings for the Southwest Airlines AI project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/southwest_ai"
)

# OpenSky API Configuration
OPENSKY_USERNAME = os.getenv("OPENSKY_USERNAME", "")
OPENSKY_PASSWORD = os.getenv("OPENSKY_PASSWORD", "")

# Data Collection Settings
# Rate limits based on authentication status
if OPENSKY_USERNAME and OPENSKY_PASSWORD:
    # Registered user limits
    MAX_REQUESTS_PER_DAY = 1000  # OpenSky API limit for registered users
    REQUEST_COOLDOWN = 5  # seconds between requests
else:
    # Anonymous user limits
    MAX_REQUESTS_PER_DAY = 100  # OpenSky API limit for anonymous users
    REQUEST_COOLDOWN = 10  # seconds between requests

# Southwest Airlines IATA code
SWA_IATA = "WN"  # Southwest Airlines IATA code

# Major Southwest Airlines Hub Airports and Focus Cities
# Using ICAO codes (required by OpenSky API)
SWA_HUBS = {
    "KATL": "Atlanta International",
    "KAUS": "Austin-Bergstrom International",
    "KBWI": "Baltimore/Washington International",
    "KBNA": "Nashville International",
    "KDAL": "Dallas Love Field",
    "KDEN": "Denver International",
    "KHOU": "Houston Hobby",
    "KLAS": "Las Vegas McCarran",
    "KLAX": "Los Angeles International",
    "KMCI": "Kansas City International",
    "KMDW": "Chicago Midway",
    "KMIA": "Miami International",
    "KMSY": "New Orleans International",
    "KOAK": "Oakland International",
    "KONT": "Ontario International",
    "KORD": "Chicago O'Hare International",
    "KPHX": "Phoenix Sky Harbor",
    "KSAN": "San Diego International",
    "KSEA": "Seattle-Tacoma International",
    "KSJC": "San Jose International",
    "KSLC": "Salt Lake City International",
    "KSTL": "St. Louis Lambert International"
}

# Radius around airports for state vectors (in degrees)
AIRPORT_RADIUS = 1.0  # Roughly 111km or 69 miles 