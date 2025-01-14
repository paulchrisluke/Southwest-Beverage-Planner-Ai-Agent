# Southwest Airlines Beverage Inventory Management System

## Overview
I've developed an AI-driven beverage inventory management system for Southwest Airlines. This system predicts beverage consumption for flights by analyzing multiple key factors including passenger demographics, route characteristics, time of day patterns, and seasonal trends. The model is designed to help optimize beverage inventory for each flight, reducing waste while ensuring passenger satisfaction.

## Features
- **Intelligent Passenger-Based Predictions**:
  - Base consumption calculated per passenger
  - Adjustments for flight duration (short/medium/long-haul)
  - Route-specific consumption patterns
  - Holiday and special event considerations

- **Route Analysis**:
  - Business vs. vacation route optimization
  - Popular route pattern recognition
  - Destination-specific consumption trends
  - Special event route handling

- **Time-Based Pattern Recognition**:
  - Morning rush preferences (high coffee, low alcohol)
  - Afternoon patterns (balanced mix)
  - Evening trends (increased alcohol, decreased hot beverages)
  - Weekend vs. weekday variations

- **Beverage Category Management**:
  - Soft Drinks: Coca-Cola, Diet Coke, Sprite, Dr Pepper, Ginger Ale
  - Hot Beverages: Coffee, Hot Tea, Hot Cocoa
  - Water/Juice: Bottled Water, Orange Juice, Cranberry Apple Juice, Tomato Juice
  - Alcoholic Beverages: Miller Lite, Dos Equis, Jack Daniels, Crown Royal, Bacardi Rum, Tito's Vodka, Baileys, Red/White Wine

- **Environmental Factors**:
  - Seasonal adjustments
  - Weather impact analysis
  - Special event considerations
  - Holiday period optimizations

## Model Intelligence
- **Passenger-Centric Approach**:
  - Base consumption rates per passenger
  - Flight duration multipliers
  - Route type adjustments
  - Time of day variations

- **Route-Based Learning**:
  - Business route patterns (higher coffee, moderate alcohol)
  - Vacation route patterns (higher overall consumption)
  - Special event routes (sports events, concerts)
  - Popular route optimization

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

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file with:
OPENWEATHER_API_KEY=your_api_key_here
```

## Usage

### Training the Model
```bash
python train_initial_model.py
```

### Starting the Server
```bash
python app.py
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