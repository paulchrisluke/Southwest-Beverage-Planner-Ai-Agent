from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import logging
from src.models.beverage_predictor import BeveragePredictor
from src.data_processing.weather_collector import WeatherCollector
import io
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Southwest Airlines Beverage Inventory Management",
    description="AI-driven beverage inventory prediction system",
    version="1.0.0"
)

# Initialize predictor and weather collector
predictor = None
weather_collector = None

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup."""
    global predictor, weather_collector
    
    try:
        predictor = BeveragePredictor()
        model_path = 'models/beverage_predictor.joblib'
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        predictor.load_model(model_path)
        logger.info("Model loaded successfully")
        
        weather_collector = WeatherCollector()
        logger.info("Weather collector initialized")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.post("/predict")
async def predict(file: UploadFile):
    """
    Make beverage consumption predictions for flights.
    Expects a CSV file with columns:
    - flight_number
    - timestamp
    - duration_hours
    - passenger_count
    - is_business_route
    - is_vacation_route
    - is_holiday
    - origin_airport
    - destination_airport
    """
    if predictor is None:
        raise HTTPException(
            status_code=500,
            detail="Model not initialized. Please try again later."
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = [
            'flight_number', 'timestamp', 'duration_hours', 'passenger_count',
            'is_business_route', 'is_vacation_route', 'is_holiday'
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
        results = []
        for idx, row in df.iterrows():
            flight_result = {
                'flight_number': row['flight_number'],
                'predictions': {}
            }
            
            # Add predictions for each category
            for category, beverages in predictions.items():
                flight_result['predictions'][category] = {}
                for beverage, values in beverages.items():
                    flight_result['predictions'][category][beverage] = int(values[idx])
            
            results.append(flight_result)
        
        return JSONResponse(content={'predictions': results})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model-info")
async def get_model_info():
    """Get information about the current model."""
    if predictor is None:
        raise HTTPException(
            status_code=500,
            detail="Model not initialized. Please try again later."
        )
    
    try:
        # Get feature importance for each beverage
        feature_importance = {}
        for category, beverages in predictor.BEVERAGE_TYPES.items():
            feature_importance[category] = {}
            for beverage in beverages:
                importance = predictor.models[beverage].feature_importances_
                feature_importance[category][beverage] = dict(zip(predictor.feature_columns, importance))
        
        return {
            'feature_columns': predictor.feature_columns,
            'beverage_types': predictor.BEVERAGE_TYPES,
            'feature_importance': feature_importance
        }
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 