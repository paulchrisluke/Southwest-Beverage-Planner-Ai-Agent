# Southwest Airlines AI Inventory Management Research

## Overview
This research project focuses on developing an AI-driven beverage inventory management system for airlines, specifically tailored for Southwest Airlines. The system aims to optimize beverage loading decisions by considering flight-specific data, historical consumption patterns, and real-time flight information.

View the full research paper and findings at: [southwest-ai.paulchrisluke.com](https://southwest-ai.paulchrisluke.com)

## Project Structure
```
.
├── app.py                 # FastAPI application for predictions
├── data/                  # Historical flight and consumption data
├── models/               # Trained ML models
├── src/                  # Source code for data processing
├── tests/                # Unit and integration tests
├── docs/                 # Documentation and research paper
└── assets/              # Web assets for GitHub Pages
```

## Features
- Real-time flight data integration using OpenSky Network API
- Machine learning models for beverage consumption prediction
- Flight-specific inventory optimization
- Historical data analysis and pattern recognition
- Web interface for data visualization and results

## Technology Stack
- Python 3.x
- FastAPI
- OpenSky Network API
- Machine Learning (scikit-learn, TensorFlow)
- GitHub Pages for research paper hosting

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

3. Run the application:
```bash
python3 app.py
```

## GitHub Pages Setup
The research paper is hosted using GitHub Pages and automatically deploys when changes are pushed to the main branch. The deployment process is handled by GitHub Actions.

### Deployment
- Automatic deployment on push to main branch
- Custom domain: [southwest-ai.paulchrisluke.com](https://southwest-ai.paulchrisluke.com)
- GitHub Actions workflow handles the build and deployment

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