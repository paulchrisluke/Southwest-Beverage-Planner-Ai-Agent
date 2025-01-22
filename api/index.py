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

# Research content
RESEARCH_CONTENT = """
<div class="research-paper">
    <h1>Southwest Airlines Beverage Predictor: A Serverless AI Solution</h1>
    
    <section class="abstract">
        <h2>Abstract</h2>
        <p>This research paper presents the development and implementation of an AI-powered beverage prediction system for Southwest Airlines, deployed on Vercel's serverless infrastructure. The system utilizes machine learning to optimize beverage inventory management and enhance passenger satisfaction through data-driven predictions.</p>
    </section>

    <section class="architecture">
        <h2>Technical Architecture</h2>
        <ul>
            <li>FastAPI backend deployed on Vercel's serverless platform</li>
            <li>Static file serving for optimized content delivery</li>
            <li>Jinja2 templating for dynamic content rendering</li>
            <li>Bootstrap 5.1.3 for responsive design</li>
            <li>Chart.js integration for data visualization</li>
        </ul>
    </section>

    <section class="key-features">
        <h2>Key Features</h2>
        <ul>
            <li>Real-time beverage demand predictions</li>
            <li>Historical consumption pattern analysis</li>
            <li>Route-specific beverage preference modeling</li>
            <li>Seasonal trend analysis</li>
            <li>Data upload capabilities for continuous model improvement</li>
        </ul>
    </section>

    <section class="implementation">
        <h2>Implementation Details</h2>
        <p>The system is built using Python with FastAPI, featuring:</p>
        <ul>
            <li>Serverless architecture for scalability</li>
            <li>Automated deployments via GitHub integration</li>
            <li>Static asset optimization</li>
            <li>Health monitoring endpoints</li>
            <li>Error logging and monitoring</li>
        </ul>
    </section>
</div>
"""

@app.get("/")
async def root(request: Request):
    try:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "research_content": RESEARCH_CONTENT}
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"error": str(e)}

@app.get("/predictions")
async def predictions(request: Request):
    return templates.TemplateResponse("predictions.html", {"request": request})

@app.get("/model-info")
async def model_info(request: Request):
    return templates.TemplateResponse("model_info.html", {"request": request})

@app.get("/docs")
async def docs_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/upload")
async def upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# This is important for Vercel serverless
app.mount = lambda *args, **kwargs: None 