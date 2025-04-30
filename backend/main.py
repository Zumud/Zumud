from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import api_router
from backend.models.db import Base, engine
from backend.utils.log import logger
import os

# Create database tables
Base.metadata.create_all(bind=engine)

logger.info("Starting FastAPI application")

app = FastAPI(
    title="Resume Tailorer API",
    description="API for Zumud - AI-powered job application assistant",
    version="1.0.0"
)

# Get allowed origins from environment or use wildcard for development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    # In production, allow the frontend domain on the same machine
    allowed_origins = [
        "http://localhost:3000",  # For local testing
        "http://localhost",       # Base URL without port
        "https://localhost",      # Secure version
        "*"                       # Allow all origins temporarily while debugging
    ]
else:
    # In development, allow all origins
    allowed_origins = ["*"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

@app.get("/", tags=["Root"])
def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the Zumud API!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
