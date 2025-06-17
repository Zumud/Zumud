from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.api import api_router
from backend.models.db import Base, engine, check_db_connection
from backend.utils.log import logger
import os

logger.info("Starting FastAPI application")

# Check database connection and create tables on startup
try:
    if check_db_connection():
        logger.info("Successfully connected to Supabase database")
        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")
    else:
        logger.error("Failed to connect to Supabase database")
        raise Exception("Database connection failed")
except Exception as e:
    logger.error(f"Database initialization error: {e}")
    # In production, you might want to exit the application
    # For now, we'll continue but log the error

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
        "database": "Supabase PostgreSQL",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint that includes database connectivity."""
    logger.info("Health check endpoint accessed")
    
    # Check database connection
    db_healthy = check_db_connection()
    
    health_status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": "1.0.0"
    }
    
    if not db_healthy:
        raise HTTPException(
            status_code=503, 
            detail="Database connection failed"
        )
    
    return health_status
