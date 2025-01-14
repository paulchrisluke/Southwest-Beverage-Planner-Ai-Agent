# Southwest Airlines Beverage Inventory Management System

## Overview
I've developed an AI-driven beverage inventory management system for Southwest Airlines. This system predicts beverage consumption for flights based on various factors such as flight duration, passenger count, route type, and seasonality.

## Features
- **Detailed Beverage Predictions**: Predicts consumption for specific beverages:
  - Soft Drinks: Coca-Cola, Diet Coke, Sprite, Dr Pepper, Ginger Ale
  - Hot Beverages: Coffee, Hot Tea, Hot Cocoa
  - Water/Juice: Bottled Water, Orange Juice, Cranberry Apple Juice, Tomato Juice
  - Alcoholic Beverages: Miller Lite, Dos Equis, Jack Daniels, Crown Royal, Bacardi Rum, Tito's Vodka, Baileys, Red/White Wine

- **Smart Predictions**: Takes into account:
  - Flight duration
  - Passenger count
  - Business vs. vacation routes
  - Holiday periods
  - Weather conditions (via OpenWeather API)

- **Real-time Weather Integration**: Uses OpenWeather API to factor in weather conditions at origin and destination airports

- **REST API Endpoints**:
  - `/predict`: Upload flight data and get beverage predictions
  - `/model-info`: Get model information and feature importance

## Project Structure
```
Southwest-AI/
├── src/
│   ├── data_processing/
│   │   ├── __init__.py
│   │   └── weather_collector.py
│   └── models/
│       ├── __init__.py
│       └── beverage_predictor.py
├── models/
│   └── beverage_predictor.joblib
├── data/
│   └── weather/          # Cached weather data
├── app.py               # FastAPI application
├── train_initial_model.py
├── view_predictions.py
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
   - timestamp
   - duration_hours
   - passenger_count
   - is_business_route (0 or 1)
   - is_vacation_route (0 or 1)
   - is_holiday (0 or 1)
   - origin_airport
   - destination_airport

2. Use the prediction endpoint:
```bash
python view_predictions.py
```

### Sample Output
```
=== Flight SWA1234 Predictions ===

Soft Drinks:
+------------+----------+
|  Beverage  | Servings |
+------------+----------+
| Coca Cola  |    36    |
| Diet Coke  |    28    |
|   Sprite   |    20    |
| Dr Pepper  |    16    |
| Ginger Ale |    4     |
+------------+----------+

[Additional categories...]
```

## Model Details

### Features Used
- `duration_hours`: Flight duration
- `passenger_count`: Number of passengers
- `is_business_route`: Business route indicator
- `is_vacation_route`: Vacation route indicator
- `is_holiday`: Holiday period indicator

### Beverage Categories and Ratios
- Soft Drinks:
  - Coca-Cola (35%)
  - Diet Coke (25%)
  - Sprite (20%)
  - Dr Pepper (15%)
  - Ginger Ale (5%)

- Hot Beverages:
  - Coffee (70%)
  - Hot Tea (20%)
  - Hot Cocoa (10%)

- Water/Juice:
  - Bottled Water (40%)
  - Orange Juice (30%)
  - Cranberry Apple Juice (20%)
  - Tomato Juice (10%)

- Alcoholic:
  - Miller Lite (20%)
  - Dos Equis (15%)
  - Jack Daniels (15%)
  - Crown Royal (10%)
  - Bacardi Rum (10%)
  - Tito's Vodka (10%)
  - Baileys (5%)
  - Red Wine (8%)
  - White Wine (7%)

### Model Behavior
- Increases beverage quantities for longer flights (>3 hours: 40% increase)
- Adjusts for vacation routes (30% more alcoholic beverages, 20% more soft drinks)
- Considers weather conditions for beverage preferences
- Accounts for holiday periods

## Testing
To test the system:
1. Start the server: `python app.py`
2. Use the sample data: `python view_predictions.py`

Sample test data is provided in `sample_prediction_data.csv`.

## Future Enhancements
- Integration with real-time flight data
- Seasonal menu adjustments
- Historical data analysis
- Inventory optimization recommendations
- Mobile app for flight attendants

## Author
Paul Chris Luke

## License
This project is proprietary and confidential. 