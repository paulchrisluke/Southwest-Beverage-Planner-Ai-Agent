# Southwest Airlines Beverage Inventory Management System

## Overview
I've developed an AI-driven beverage inventory management system for Southwest Airlines. This system predicts beverage consumption by prioritizing passenger-centric factors (load factors, route types, flight timing) while incorporating secondary environmental factors like weather conditions. The model optimizes beverage inventory for each flight, ensuring passenger satisfaction while minimizing waste.

## Features
- **Core Passenger-Based Predictions**:
  - Passenger count as primary predictor
  - Load factor analysis (typically 75-85%)
  - Per-passenger consumption baselines
  - Group travel pattern recognition
  - Flight duration impact analysis

- **Route and Time Analysis**:
  - Business vs. vacation route patterns
  - Time-of-day consumption trends
  - Flight duration categories
  - Historical route performance
  - Special event and holiday adjustments

- **Time-Based Pattern Recognition**:
  - Morning rush preferences (high coffee, low alcohol)
  - Afternoon patterns (balanced mix)
  - Evening trends (increased alcohol, decreased hot beverages)
  - Weekend vs. weekday variations

- **Secondary Environmental Factors**:
  - Weather impact assessment
  - Seasonal trend analysis
  - Special event considerations
  - Holiday period adjustments

## Model Intelligence
- **Primary Predictors (70-80% impact)**:
  - Passenger count and demographics
  - Flight duration and timing
  - Route type and historical patterns
  - Day of week and time of day

- **Secondary Factors (20-30% impact)**:
  - Weather conditions
  - Seasonal variations
  - Special events
  - Holiday periods

- **Time-Based Distribution**:
  Morning (6-11 AM):
  - Hot Beverages: 40%
  - Soft Drinks: 25%
  - Water/Juice: 30%
  - Alcoholic: 5%

  Afternoon (11 AM-4 PM):
  - Hot Beverages: 15%
  - Soft Drinks: 40%
  - Water/Juice: 30%
  - Alcoholic: 15%

  Evening (4 PM-9 PM):
  - Hot Beverages: 10%
  - Soft Drinks: 35%
  - Water/Juice: 25%
  - Alcoholic: 30%

  Night (9 PM-6 AM):
  - Hot Beverages: 20%
  - Soft Drinks: 30%
  - Water/Juice: 35%
  - Alcoholic: 15%

## Project Structure
```
Southwest-AI/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── weather_collector.py    # Weather data collection
│   └── models/
│       ├── __init__.py
│       └── beverage_predictor.py   # ML model implementation
├── tests/
│   └── test_weather_integration.py # Integration tests
├── data/
│   └── weather_cache/             # Cached weather data
├── app.py                         # FastAPI application
├── train_initial_model.py         # Model training script
├── view_predictions.py            # Prediction viewer
└── requirements.txt
```

## Installation
1. Clone the repository:
```bash
git clone https://github.com/paulchrisluke/Southwest-AI.git
cd Southwest-AI
```


3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with:
OPENWEATHER_API_KEY=your_api_key_here
OPENSKY_PASSWORD=
OPENWEATHER_API_KEY=
```

## Usage

### Training the Model
```bash
python train_initial_model.py
```

### Starting the Server
```bash
python app.py
uvicorn app:app --reload
```

### Making Predictions
1. Prepare a CSV file with the following columns:
   - flight_number
   - timestamp (Unix timestamp)
   - duration_hours
   - passenger_count
   - is_business_route (0 or 1)
   - is_vacation_route (0 or 1)
   - is_holiday (0 or 1)
   - origin_airport (ICAO code)
   - destination_airport (ICAO code)

2. Use the prediction endpoint:
```bash
python view_predictions.py
```

## Model Details

### Core Prediction Factors
- **Passenger Analysis**:
  - Base consumption per passenger
  - Flight duration multipliers
  - Route type adjustments
  - Group travel patterns

- **Route Characteristics**:
  - Business routes: +30% coffee, -10% alcohol
  - Vacation routes: +30% overall consumption
  - Holiday routes: +20% all categories
  - Special event routes: Custom adjustments

- **Time-Based Patterns**:
  - Morning peak for hot beverages
  - Evening peak for alcoholic beverages
  - Weekend alcohol consumption +20%
  - Holiday period adjustments

### Model Performance
- Passenger count and route type are primary predictors
- Time of day shows strong correlation with beverage choices
- Route characteristics influence overall consumption
- Weather acts as a secondary modifier

## Testing
The system includes comprehensive tests for:
- Passenger-based consumption patterns
- Route-specific predictions
- Time-of-day distribution accuracy
- Special event handling
- Weather impact verification

Run tests with:
```bash
python -m pytest tests/
```

## Future Enhancements
- Enhanced passenger demographic analysis
- Route popularity scoring
- Special event detection and prediction
- Group travel pattern recognition
- Real-time inventory optimization
- Mobile app for flight attendants
- Machine learning improvements:
  - Deep learning for pattern recognition
  - Time series analysis
  - Enhanced route analysis

## Author
Paul Chris Luke

## License
This project is proprietary and confidential. 