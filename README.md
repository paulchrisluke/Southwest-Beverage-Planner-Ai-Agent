# Southwest Airlines Beverage Inventory Management AI

Research project focused on AI-driven optimization of beverage inventory management for airlines, using historical flight data to predict and optimize beverage loads for individual flights.

## Data Sources

This research uses flight tracking data from the OpenSky Network. For required citations and data usage terms, please see [CITATION.md](CITATION.md).

## Project Structure

```
.
├── data/               # Data storage
│   └── historical/    # Historical flight data
├── src/               # Source code
│   ├── config/       # Configuration settings
│   ├── data_collection/ # Data collection modules
│   └── models/       # Database models
├── tests/             # Test files
└── migrations/        # Database migrations
```

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables in `.env`:
```
DATABASE_URL=postgresql://localhost:5432/southwest_ai
OPENSKY_USERNAME=your_username  # Optional
OPENSKY_PASSWORD=your_password  # Optional
```

4. Initialize the database:
```bash
createdb southwest_ai
alembic upgrade head
```

## Data Collection

The project collects historical flight data from the OpenSky Network for Southwest Airlines flights at major hubs and focus cities. Data is collected in 2-hour chunks and saved incrementally to allow for interruption and resumption.

To start data collection:
```bash
python src/data_collection/collector_daemon.py
```

## License

This project is for research purposes only. Flight data is provided by the OpenSky Network and is subject to their terms of use. 