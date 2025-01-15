# Southwest Airlines AI Inventory Management Research

## Overview
This research project focuses on developing an AI-driven beverage inventory management system for airlines, specifically tailored for Southwest Airlines. The system aims to optimize beverage loading decisions by considering flight-specific data, historical consumption patterns, and real-time flight information.

View the full research paper and findings at: [southwest-ai.paulchrisluke.com](https://southwest-ai.paulchrisluke.com)

## Project Structure
```
.
├── app.py                 # FastAPI application for predictions
├── data/                  # Historical flight and consumption data
│   └── historical/       # Collected flight data in JSON format
├── models/               # Trained ML models
│   └── beverage_predictor.joblib  # Trained prediction model
├── src/                  # Source code for data processing
│   ├── models/          # ML model implementations
│   └── data_collection/ # Data collection scripts
├── tests/                # Unit and integration tests
├── docs/                # Documentation and research paper
└── assets/              # Web assets for GitHub Pages
```

## Features
- Real-time flight data integration using OpenSky Network API
- Machine learning models for beverage consumption prediction
- Flight-specific inventory optimization
- Historical data analysis and pattern recognition
- Web interface for data visualization and results
- Static API endpoints for flight data and predictions

## Technology Stack
- Python 3.x
- FastAPI (development)
- Static API (production)
- OpenSky Network API
- Machine Learning (scikit-learn)
- GitHub Pages for hosting

## Static API Endpoints
The project uses a static API architecture for production, with endpoints generated during build:

- `/api/dates.json` - Available flight dates
- `/api/flights/{date}.json` - Flights for a specific date
- `/api/predictions/{flight_id}.json` - Predictions for a specific flight

## Model Training
The beverage prediction model is trained on historical flight data:

1. Train the model:
```bash
cd src/models
python3 train_model.py
```

2. The script will:
   - Process sample flight data
   - Train a RandomForest model
   - Save the model to `models/beverage_predictor.joblib`

## Local Development
1. Clone the repository:
```bash
git clone https://github.com/paulchrisluke/Southwest-AI.git
cd Southwest-AI
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. For development with live API:
```bash
python3 app.py
```

4. For static site preview:
```bash
python3 -m http.server 8000
```

## GitHub Pages Deployment
The site is hosted using GitHub Pages with automatic deployment:

### Build Process
1. Generates static API responses from historical data
2. Pre-computes predictions using the trained model
3. Creates JSON files for all endpoints
4. Deploys to GitHub Pages

### Deployment Triggers
- Automatic deployment on push to main branch
- Manual trigger via GitHub Actions
- Custom domain: [southwest-ai.paulchrisluke.com](https://southwest-ai.paulchrisluke.com)

## Data Collection
Flight data is collected automatically:
- Runs twice monthly (1st and 15th)
- Collects from major Southwest hubs
- Stores in `data/historical/` as JSON
- Handles rate limits and API cooldown

## Contributing
This is a personal research project by Paul Chris Luke. While it's open source for educational purposes, I'm not actively seeking contributions at this time.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author
Paul Chris Luke
- Website: [paulchrisluke.com](https://paulchrisluke.com)
- GitHub: [@paulchrisluke](https://github.com/paulchrisluke)

## Acknowledgments
- Southwest Airlines for inspiring this research
- OpenSky Network for providing flight data API
- My college friend for providing beverage inventory data 