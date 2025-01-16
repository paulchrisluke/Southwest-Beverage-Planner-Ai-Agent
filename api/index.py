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

# Setup templates
try:
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates directory configured successfully")
except Exception as e:
    logger.error(f"Error configuring templates: {e}")

@app.get("/api/test")
async def test():
    logger.info("Test endpoint called")
    return {
        "status": "ok",
        "message": "API is working",
        "cwd": os.getcwd(),
        "dir_contents": os.listdir('.')
    }

@app.get("/")
async def root(request: Request):
    logger.info("Root endpoint called")
    try:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "research_content": "Welcome to Southwest Airlines Beverage Predictor"
        })
    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

def handler(request, context):
    return app 