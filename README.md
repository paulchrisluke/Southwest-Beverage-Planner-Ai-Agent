# Southwest Airlines AI-Driven Beverage Inventory Management

## Overview
I am developing an AI-driven inventory management system for optimizing beverage stock on Southwest Airlines flights. This project analyzes historical beverage consumption data and provides intelligent restocking recommendations based on route characteristics, seasonal patterns, passenger behavior, and weather conditions.

## Key Features
- **Intelligent Prediction**: Machine learning model that considers:
  - Route characteristics (business/vacation routes)
  - Seasonal patterns (summer/winter consumption)
  - Weather conditions at airports
  - Holiday and peak travel periods
  - Historical consumption patterns

- **Data Processing**:
  - OpenSky Network API integration for flight data
  - Weather data collection and caching
  - CSV data validation and cleaning
  - Excel file conversion support

- **Automated Training Pipeline**:
  - Scheduled model retraining
  - Performance monitoring
  - Data validation
  - Automated backups
  - Configurable training parameters

## Project Structure
```
Southwest-AI/
├── config/                 # Configuration files
│   └── training_config.json
├── data/
│   ├── historical/        # Historical flight data
│   ├── training/         # Training data files
│   ├── weather/          # Cached weather data
│   └── consumption/      # Generated consumption data
├── docs/                 # Documentation
│   ├── data_format.md
│   └── excel_conversion.md
├── logs/                 # Application logs
├── models/              # Trained models
├── scripts/             # Utility scripts
│   └── run_training_service.py
├── src/
│   ├── data_processing/
│   │   ├── validate_csv.py
│   │   ├── excel_converter.py
│   │   ├── weather_collector.py
│   │   └── seasonal_analyzer.py
│   ├── models/
│   │   ├── predictor.py
│   │   ├── retrain.py
│   │   └── training_pipeline.py
│   └── api/
│       └── main.py
└── tests/               # Unit tests
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Southwest-AI.git
cd Southwest-AI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### Data Collection
1. Generate synthetic data:
```bash
python src/data_processing/beverage_data_generator.py
```

2. Convert Excel files:
```bash
python src/data_processing/excel_converter.py input.xlsx
```

### Model Training
1. One-time training:
```bash
python src/models/training_pipeline.py
```

2. Run training service:
```bash
# Foreground mode
python scripts/run_training_service.py

# Daemon mode
python scripts/run_training_service.py --daemon
```

### Making Predictions
1. Start the API server:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

2. Upload data and get predictions:
```bash
curl -X POST http://localhost:8000/predict -F "file=@flight_data.csv"
```

## Configuration

### Training Configuration
Edit `config/training_config.json` to customize:
- Training schedule
- Validation thresholds
- Model parameters
- Backup settings
- Notification preferences

Example configuration:
```json
{
    "training_schedule": {
        "frequency": "daily",
        "time": "02:00"
    },
    "performance_threshold": 0.8,
    "min_training_samples": 1000
}
```

### Data Validation
The system validates:
- Flight numbers (must start with SWA)
- Passenger counts (143 or 175)
- Duration (0.5 to 8.0 hours)
- Consumption amounts (per passenger limits)
- Required data fields

## Model Features

### Base Features
- Flight duration
- Passenger count
- Route type (business/vacation)
- Time of day
- Day of week

### Weather Features
- Temperature
- Humidity
- Precipitation
- Wind speed
- Adverse weather conditions

### Seasonal Features
- Season (winter/summer)
- Holiday periods
- Peak travel times
- Special events

## Performance Monitoring
The system tracks:
- Model R² score
- Per-beverage accuracy
- Prediction errors
- Training success rate
- Data quality metrics

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is open source and available under the MIT License.

## Acknowledgments
- OpenSky Network for flight data
- OpenWeatherMap for weather data
- Southwest Airlines for inspiration

## Contact
Paul Chris Luke - [Your Email]
Project Link: [GitHub Repository URL] 