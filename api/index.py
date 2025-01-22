from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Get the absolute path to the templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/")
async def root(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "research_content": "Welcome to Southwest Airlines Beverage Predictor"}
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# This is important for Vercel serverless
app.mount = lambda *args, **kwargs: None 