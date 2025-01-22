from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

# Log environment for debugging
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")
logger.info(f"Environment variables: {dict(os.environ)}")

try:
    # Setup templates directory
    templates = Jinja2Templates(directory="templates")
    logger.info("Templates directory configured")
except Exception as e:
    logger.error(f"Error setting up templates: {e}")
    raise

# Mount static files
STATIC_DIR = Path(__file__).parent.parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

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
            content={
                "error": str(e),
                "cwd": os.getcwd(),
                "dir_contents": os.listdir('.')
            },
            status_code=500
        )

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Handler for Vercel serverless
def handler(request, context):
    return app 