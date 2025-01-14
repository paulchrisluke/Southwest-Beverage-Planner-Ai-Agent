import os
import logging
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import json
from src.models.beverage_predictor import BeveragePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Southwest Airlines Beverage Predictor",
    description="AI-driven beverage inventory management system",
    version="1.0.0"
)

# Initialize predictor as None - will be loaded during startup
predictor = None

@app.on_event("startup")
async def startup_event():
    """Initialize the model during startup"""
    global predictor
    try:
        model_path = 'models/beverage_predictor.joblib'
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        predictor = BeveragePredictor()
        predictor.load_model(model_path)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize model")

@app.post("/predict")
async def predict(file: UploadFile):
    """Make predictions for flights in the uploaded CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    if predictor is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    try:
        # Read CSV file
        df = pd.read_csv(file.file)
        required_columns = [
            'flight_number', 'timestamp', 'duration_hours', 'passenger_count',
            'is_business_route', 'is_vacation_route', 'is_holiday',
            'origin_airport', 'destination_airport'
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Make predictions
        predictions = predictor.predict(df)
        
        # Format response
        response = []
        for i, pred_str in enumerate(predictions):
            flight_data = {
                'flight_number': df.iloc[i]['flight_number'],
                'predictions': json.loads(pred_str)
            }
            response.append(flight_data)
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error making predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
async def get_model_info():
    """Get information about the current model"""
    if predictor is None:
        raise HTTPException(status_code=500, detail="Model not initialized")
    
    try:
        feature_importance = predictor.get_feature_importance()
        return {
            'feature_importance': feature_importance,
            'feature_columns': predictor.feature_columns,
            'beverage_categories': predictor.beverage_categories
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 