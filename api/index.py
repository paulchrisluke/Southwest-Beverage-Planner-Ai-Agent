from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
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