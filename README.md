# Southwest Airlines AI-Driven Beverage Inventory Management

This research project aims to optimize beverage inventory management for Southwest Airlines flights using AI and real-time flight data. The project focuses on US domestic flights and utilizes free, publicly available data sources.

## Data Sources

### Flight Data (OpenSky Network)
- Anonymous access (400 requests/day limit)
- Filtering for Southwest Airlines (ICAO: SWA)
- US domestic flights only
- Data points collected:
  - Flight numbers
  - Departure/arrival times
  - Routes
  - Aircraft types

### Weather Data (National Weather Service API)
- Free, unlimited access
- US coverage
- Current conditions and forecasts
- No API key required

### Beverage Consumption Data
- Support for real consumption data input
- Standardized CSV/JSON format
- Data schema:
  ```
  flight_number,date,departure,arrival,beverage_type,initial_count,final_count
  ```
- Automated data validation and integration
- Synthetic data generation for gaps

## Data Collection Strategy

### Daily Batch Processing
1. Collect SWA flights data within US airspace
2. Process in 24-hour blocks
3. Store in local database
4. Account for 400 requests/day limit

### Rate Limiting
- Maximum 400 API calls per day (OpenSky)
- Implemented cooldown periods between requests
- Batch processing during off-peak hours

## Project Setup

### Requirements
```
python>=3.8
requests
pandas
numpy
scikit-learn
opensky-api
```

### Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure data collection parameters in `config.py`

## Quick Start for Airline Data Providers

### Upload Your Data
1. Prepare your beverage consumption CSV file:
   ```
   flight_number,date,departure,arrival,beverage_type,initial_count,final_count
   WN1234,2024-03-20,LAX,PHX,coffee,100,85
   WN1234,2024-03-20,LAX,PHX,water,150,120
   ```

2. Access the Web Interface
   - Visit: `https://swa-beverage-ai.oracle.app`
   - Upload your CSV file
   - Get immediate visualization of:
     - Predicted vs. Actual consumption
     - Potential savings per route
     - Weight reduction opportunities
     - Stockout risk analysis

3. View Results
   - Interactive dashboard showing:
     - Route-specific recommendations
     - Daily/weekly trends
     - Cost saving estimates
     - Environmental impact

### Sample Results
```
Flight WN1234 (LAX-PHX)
✓ Reduce coffee load by: 10 units
✓ Estimated weight savings: 2.5 lbs
✓ Projected annual savings: $1,200
✓ Stockout risk: <1%
```

## Deployment

### Infrastructure (Oracle Cloud Free Tier)
- 2 Always Free AMD compute instances
- PostgreSQL database
- Automated deployment via GitHub Actions
- Monitoring and alerting setup

### Quick Deploy
1. Fork this repository
2. Set up Oracle Cloud Free Tier account
3. Configure GitHub secrets:
   ```
   ORACLE_CLOUD_USER
   ORACLE_CLOUD_KEY
   DB_CONNECTION_STRING
   ```
4. Run deployment workflow
5. Monitor status in GitHub Actions

### Monitoring
- System health dashboard
- API usage tracking
- Data collection logs
- Model performance metrics

## Research Limitations
- Data collection limited by OpenSky anonymous access
- US domestic flights only
- Potential coverage gaps in certain regions
- 24-hour delay in data processing due to rate limits

## Contributing
This is an open-source research project. Contributions are welcome through pull requests. 