# Testing Documentation

## Overview
This document outlines the testing procedures and scenarios for the Southwest Airlines Beverage Inventory Management System.

## Test Components

### 1. Weather Data Collection
- **Test File**: `test_weather.py`
- **Purpose**: Verify weather data collection for airports
- **Test Cases**:
  - Fetch weather for KLAS (Las Vegas)
  - Fetch weather for KMDW (Chicago)
  - Fetch weather for KATL (Atlanta)
- **Validation**:
  - Temperature (°F)
  - Humidity (%)
  - Wind Speed (mph)
  - Precipitation (mm)
  - Weather Condition
  - Adverse Weather Flag

### 2. Beverage Prediction Model
- **Test File**: `train_initial_model.py`
- **Purpose**: Train and validate the prediction model
- **Test Cases**:
  - Generate synthetic training data
  - Train models for each beverage
  - Validate feature importance
- **Model Metrics**:
  ```
  Feature Importance Example (Coca Cola):
  - duration_hours: 0.6184
  - passenger_count: 0.2536
  - is_vacation_route: 0.0676
  - is_business_route: 0.0324
  - is_holiday: 0.0279
  ```

### 3. API Endpoints
- **Test File**: `view_predictions.py`
- **Purpose**: Test prediction API functionality
- **Endpoints**:
  1. `/predict` (POST)
     - Input: CSV file
     - Output: Beverage predictions by category
  2. `/model-info` (GET)
     - Output: Model configuration and feature importance

## Test Scenarios

### 1. Business Route Flight
```csv
flight_number,timestamp,duration_hours,passenger_count,is_business_route,is_vacation_route,is_holiday
SWA1234,1706745600,2.5,143,1,0,0
```
Expected behavior:
- Moderate alcohol consumption
- High coffee consumption
- Standard soft drink distribution

### 2. Vacation Route Flight
```csv
flight_number,timestamp,duration_hours,passenger_count,is_business_route,is_vacation_route,is_holiday
SWA5678,1706832000,3.75,175,0,1,0
```
Expected behavior:
- Higher alcohol consumption (+30%)
- Higher soft drink consumption (+20%)
- Lower coffee consumption

### 3. Holiday Flight
```csv
flight_number,timestamp,duration_hours,passenger_count,is_business_route,is_vacation_route,is_holiday
SWA9012,1706918400,1.5,143,0,0,1
```
Expected behavior:
- Balanced beverage distribution
- Seasonal beverage adjustments
- Standard consumption patterns

## Sample Test Results

### Flight SWA1234 (Business Route)
```
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

Hot Beverages:
+-----------+----------+
| Beverage  | Servings |
+-----------+----------+
|  Coffee   |    38    |
|  Hot Tea  |    9     |
| Hot Cocoa |    6     |
+-----------+----------+
```

### Flight SWA5678 (Vacation Route)
```
Alcoholic:
+--------------+----------+
|   Beverage   | Servings |
+--------------+----------+
| Miller Lite  |    11    |
| Jack Daniels |    9     |
|  Dos Equis   |    8     |
| Crown Royal  |    8     |
| Bacardi Rum  |    6     |
| Titos Vodka  |    6     |
|   Red Wine   |    5     |
|  White Wine  |    4     |
|   Baileys    |    2     |
+--------------+----------+
```

## Running Tests

1. Start the server:
```bash
python app.py
```

2. Run prediction tests:
```bash
python view_predictions.py
```

3. Test weather collection:
```bash
python test_weather.py
```

## Validation Criteria

### Data Validation
- Flight numbers follow SWA format
- Valid airport codes
- Reasonable passenger counts (100-200)
- Valid timestamps
- Boolean flags (0 or 1)

### Prediction Validation
- Non-negative quantities
- Reasonable serving numbers
- Category total ratios
- Route-specific adjustments
- Duration-based scaling

## Known Limitations
1. Weather data is current only (no historical)
2. Limited to specific airport set
3. No real-time flight data integration
4. Synthetic training data
5. Fixed beverage menu

## Future Test Cases
1. Seasonal variation testing
2. Extreme weather scenarios
3. Special event flights
4. Multiple-leg journeys
5. Equipment variation impact
``` 