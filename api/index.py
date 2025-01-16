from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from pathlib import Path

app = FastAPI()

# Get the absolute path to the templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/api")
async def read_root():
    return {"message": "Hello from FastAPI"}

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "research_content": "Welcome to Southwest Airlines Beverage Predictor"
    })

# This is required for Vercel serverless functions
from mangum import Adapter
handler = Adapter(app) 