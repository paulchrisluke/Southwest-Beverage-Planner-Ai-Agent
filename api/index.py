from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Log the current directory and environment
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
logger.info(f"Environment variables: {dict(os.environ)}")

# Get the absolute path to the templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
logger.info(f"Templates directory path: {TEMPLATES_DIR}")
logger.info(f"Templates directory exists: {TEMPLATES_DIR.exists()}")
if TEMPLATES_DIR.exists():
    logger.info(f"Templates directory contents: {list(TEMPLATES_DIR.iterdir())}")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/api/test")
async def test():
    logger.info("Test endpoint called")
    return {
        "status": "ok",
        "message": "API is working",
        "environment": os.getenv("VERCEL_ENV", "unknown"),
        "cwd": os.getcwd(),
        "templates_dir": str(TEMPLATES_DIR),
        "templates_exists": TEMPLATES_DIR.exists()
    }

@app.get("/api")
async def read_root():
    logger.info("API endpoint called")
    return {"message": "Hello from FastAPI"}

@app.get("/")
async def root(request: Request):
    logger.info("Root endpoint called")
    try:
        response = templates.TemplateResponse("index.html", {
            "request": request,
            "research_content": "Welcome to Southwest Airlines Beverage Predictor"
        })
        logger.info("Template response created successfully")
        return response
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

# This is required for Vercel serverless functions
from mangum import Adapter

# Create handler with custom configurations
handler = Adapter(app, lifespan="off") 