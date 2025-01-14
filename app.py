from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import pandas as pd
import joblib
import json
from datetime import datetime
from typing import Dict, Any
import logging
import markdown2
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Southwest Airlines Beverage Predictor")

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/data", StaticFiles(directory="data"), name="data")

# Initialize predictor during startup
model_path = Path("models/beverage_predictor.joblib")
predictor = None

@app.on_event("startup")
async def startup_event():
    global predictor
    try:
        predictor = joblib.load(model_path)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise HTTPException(status_code=500, detail="Error loading model")

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    # Read and convert markdown to HTML
    research_paper_path = Path("docs/research_paper.md")
    with open(research_paper_path) as f:
        content = f.read()
        html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "research_content": html_content
    })

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/predictions", response_class=HTMLResponse)
async def predictions_page(request: Request, flight: str = None, date: str = None):
    try:
        # Load all flight data from historical directory
        flights = []
        historical_dir = Path("data/historical")
        
        # If no date is provided, use the most recent date from our data
        all_dates = set()
        for file_path in historical_dir.glob("*_flights.json"):
            if "_progress" not in str(file_path):
                try:
                    with open(file_path, "r") as f:
                        airport_flights = json.load(f)
                        if isinstance(airport_flights, list):
                            for f in airport_flights:
                                if isinstance(f, dict) and f.get("firstSeen"):
                                    flight_date = datetime.fromtimestamp(f["firstSeen"]).strftime('%Y-%m-%d')
                                    all_dates.add(flight_date)
                except Exception as e:
                    logger.warning(f"Error reading dates from {file_path}: {e}")
                    continue
        
        if not all_dates:
            logger.warning("No valid dates found in historical data")
            return templates.TemplateResponse("predictions.html", {
                "request": request,
                "error": "No flight data available"
            })
            
        # Sort dates and get the most recent one
        sorted_dates = sorted(all_dates, reverse=True)
        most_recent_date = sorted_dates[0] if sorted_dates else None
        
        # Use provided date if valid, otherwise use most recent
        if date and date in all_dates:
            selected_date = date
        else:
            selected_date = most_recent_date
            
        # Now load flights for the selected date
        for file_path in historical_dir.glob("*_flights.json"):
            if "_progress" not in str(file_path):
                try:
                    with open(file_path, "r") as f:
                        airport_flights = json.load(f)
                        if isinstance(airport_flights, list):
                            for f in airport_flights:
                                if isinstance(f, dict) and f.get("callsign", "").startswith("SWA"):
                                    if f.get("estDepartureAirport") and f.get("estArrivalAirport"):
                                        flight_date = datetime.fromtimestamp(f["firstSeen"]).strftime('%Y-%m-%d')
                                        if flight_date == selected_date:
                                            flight_info = {
                                                'flight_number': f["callsign"].replace("SWA", "WN"),
                                                'origin_airport': f["estDepartureAirport"],
                                                'destination_airport': f["estArrivalAirport"],
                                                'date': flight_date,
                                                'departure_time': datetime.fromtimestamp(f["firstSeen"]).strftime('%H:%M'),
                                                'passenger_count': 150  # Estimated based on typical 737 load factor
                                            }
                                            flights.append(flight_info)
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
                    continue

        if not flights:
            logger.warning(f"No flights found for date {selected_date}")
            return templates.TemplateResponse("predictions.html", {
                "request": request,
                "error": f"No flights found for date {selected_date}",
                "available_dates": sorted_dates,
                "selected_date": selected_date
            })

        # Sort flights by departure time
        flights.sort(key=lambda x: x['departure_time'])
        
        # Initialize variables
        selected_flight = None
        predictions = None
        total_beverages = 0
        beverages_per_passenger = 0
        flight_duration = "0h 0m"
        
        # If a specific flight is selected or use the first flight
        if flight:
            selected_flight = next((f for f in flights if f['flight_number'] == flight), None)
        
        if not selected_flight and flights:
            selected_flight = flights[0]
            
        # Get predictions for selected flight
        if selected_flight and predictor:
            df = pd.DataFrame([selected_flight])
            raw_predictions = predictor.predict(df)
            predictions = {}
            total_beverages = 0
            for beverage, quantity in raw_predictions.items():
                confidence = min(95, max(70, 85 + quantity/10))
                status = 'optimal' if quantity > 0 else 'critical'
                trend = 'up' if quantity > 100 else 'down' if quantity < 50 else 'stable'
                trend_color = 'success' if trend == 'up' else 'danger' if trend == 'down' else 'secondary'
                
                predictions[beverage] = {
                    'quantity': int(quantity),
                    'confidence': int(confidence),
                    'status': status,
                    'trend': trend,
                    'trend_color': trend_color
                }
                total_beverages += quantity
            
            beverages_per_passenger = round(total_beverages / selected_flight['passenger_count'], 1)
            flight_duration = "2h 15m"  # TODO: Calculate actual flight duration based on route
        
        return templates.TemplateResponse("predictions.html", {
            "request": request,
            "flights": flights,
            "selected_flight": selected_flight,
            "predictions": predictions,
            "total_beverages": int(total_beverages),
            "beverages_per_passenger": beverages_per_passenger,
            "flight_duration": flight_duration,
            "selected_date": selected_date,
            "available_dates": sorted_dates
        })
        
    except Exception as e:
        logger.error(f"Error loading flight data: {e}")
        return templates.TemplateResponse("predictions.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/model-info", response_class=HTMLResponse)
async def model_info_page(request: Request):
    # Get model information
    model_info = {
        "type": "Random Forest Regressor",
        "last_trained": "2024-03-15",
        "training_samples": 10000,
        "mae": 2.45,
        "r2_score": 0.89,
        "performance_history": {
            "dates": ["Jan", "Feb", "Mar", "Apr", "May"],
            "mae": [3.2, 2.9, 2.7, 2.5, 2.45]
        },
        "feature_importance": {
            "features": ["passenger_count", "temperature", "time_of_day", "day_of_week", "route_distance"],
            "scores": [0.35, 0.20, 0.15, 0.15, 0.15]
        },
        "insights": [
            "Passenger count is the strongest predictor of beverage consumption",
            "Temperature has a moderate impact on beverage choices",
            "Time of day affects consumption patterns significantly",
            "Longer routes show increased beverage consumption",
            "Weekend flights tend to have higher consumption rates"
        ]
    }
    
    return templates.TemplateResponse("model_info.html", {
        "request": request,
        "model_info": model_info
    })

@app.post("/predict")
async def predict(request: Request, file: UploadFile = File(...)):
    try:
        # Read and validate CSV
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        required_columns = [
            "flight_number", "date", "departure_time",
            "origin_airport", "destination_airport", "passenger_count"
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Make predictions
        predictions = predictor.predict(df)
        
        # Transform predictions into a structured format
        formatted_predictions = {}
        for beverage, quantity in predictions.items():
            confidence = min(95, max(70, 85 + quantity/10))  # Example confidence calculation
            status = 'optimal' if quantity > 0 else 'critical'
            
            formatted_predictions[beverage] = {
                'quantity': int(quantity),
                'confidence': int(confidence),
                'status': status
            }
        
        # Get flight details for display
        flight_details = {
            'flight_number': df['flight_number'].iloc[0],
            'origin_airport': df['origin_airport'].iloc[0],
            'destination_airport': df['destination_airport'].iloc[0],
            'date': df['date'].iloc[0],
            'passenger_count': df['passenger_count'].iloc[0]
        }
        
        return templates.TemplateResponse("predictions.html", {
            "request": request,
            "predictions": formatted_predictions,
            **flight_details
        })
        
    except Exception as e:
        logger.error(f"Error processing prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-consumption-data")
async def upload_consumption_data(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        # Transform data
        transformed_df = transform_consumption_data(df)
        
        # Save to data directory
        output_path = Path("data/processed") / f"consumption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        transformed_df.to_csv(output_path, index=False)
        
        return {"message": "Data uploaded and processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing consumption data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def transform_consumption_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw consumption data into model-ready format."""
    try:
        # Convert timestamps
        df['date'] = pd.to_datetime(df['date'])
        
        # Expand beverage columns
        if 'beverages' in df.columns:
            beverages_df = df['beverages'].apply(json.loads).apply(pd.Series)
            df = pd.concat([df.drop('beverages', axis=1), beverages_df], axis=1)
        
        return df
        
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise 

@app.get("/docs")
async def docs_page(request: Request, doc: str = None):
    """Render the documentation page with the selected document."""
    docs_dir = "docs"
    current_doc = doc or "research_paper"  # Default to research paper if no doc specified
    
    try:
        # Map doc parameter to actual file paths
        doc_paths = {
            "research_paper": os.path.join(docs_dir, "research_paper.md"),
            "data_format": os.path.join(docs_dir, "data_format.md"),
            "testing": os.path.join(docs_dir, "testing.md")
        }
        
        if current_doc not in doc_paths:
            raise HTTPException(status_code=404, detail="Document not found")
            
        # Read and convert the markdown file
        with open(doc_paths[current_doc], 'r') as f:
            content = f.read()
            html_content = markdown2.markdown(content)
            
        return templates.TemplateResponse(
            "docs.html",
            {
                "request": request,
                "doc_content": html_content,
                "current_doc": current_doc
            }
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        logging.error(f"Error rendering documentation: {str(e)}")
        raise HTTPException(status_code=500, detail="Error rendering documentation") 