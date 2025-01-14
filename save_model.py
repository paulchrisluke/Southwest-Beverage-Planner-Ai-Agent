import joblib
from src.models.beverage_predictor import BeveragePredictor

# Create and save a dummy model
predictor = BeveragePredictor()
joblib.dump(predictor, 'models/beverage_predictor.joblib') 