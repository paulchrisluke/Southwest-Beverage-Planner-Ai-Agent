from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
import sys
import os
from typing import Dict, List
import logging

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.predictor import BeveragePredictor

app = FastAPI(
    title="Southwest Airlines Beverage Inventory AI",
    description="AI-driven beverage inventory management system",
    version="1.0.0"
)

# Initialize the predictor
predictor = None
try:
    predictor = BeveragePredictor.load_model('models/beverage_predictor.joblib')
    logging.info("Loaded existing model")
except:
    predictor = BeveragePredictor()
    logging.info("Initialized new model")

@app.post("/upload-data")
async def upload_data(file: UploadFile = File(...)):
    """Upload CSV data for training or prediction."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, detail="Only CSV files are supported")
    
    try:
        # Read CSV content
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        required_columns = [
            'flight_number',
            'timestamp',
            'duration_hours',
            'passenger_count',
            'is_business_route',
            'is_vacation_route'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        return {"message": "Data uploaded successfully", "rows": len(df)}
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Get beverage consumption predictions for uploaded flight data."""
    if not predictor:
        raise HTTPException(500, detail="Model not initialized")
    
    try:
        # Read CSV content
        contents = await file.read()
        flight_data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Make predictions
        predictions = predictor.predict(flight_data)
        
        # Format response
        response_data = []
        for i, row in flight_data.iterrows():
            response_data.append({
                "flight_number": row["flight_number"],
                "predictions": {
                    "soft_drinks": int(predictions[i][0]),
                    "hot_beverages": int(predictions[i][1]),
                    "water_juice": int(predictions[i][2]),
                    "alcoholic": int(predictions[i][3])
                }
            })
        
        return JSONResponse(content={"predictions": response_data})
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/model-info")
async def model_info():
    """Get information about the current model."""
    if not predictor:
        raise HTTPException(500, detail="Model not initialized")
    
    return {
        "feature_importance": predictor.get_feature_importance(),
        "features": predictor.feature_columns
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 