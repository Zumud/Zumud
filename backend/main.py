import os

# Sentry setup for API monitoring
import sentry_sdk
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from backend.api import api_router
from backend.models.db import Base, check_db_connection, engine
from backend.utils.log import logger

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),  # You'll need to set this in your environment
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    profiles_sample_rate=1.0,  # Capture 100% of profiles for performance monitoring
    environment=os.getenv("ENVIRONMENT", "development"),
    # Set this to False in production to avoid sending PII
    send_default_pii=True,
)

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
    version="1.0.0",
)

# Allowed CORS origins = the frontend sites whose browser JS may read API
# responses. NOT a wildcard in production: only our own frontend should be
# permitted (a wildcard also can't be combined with allow_credentials).
# Override with CORS_ALLOWED_ORIGINS (comma-separated) if domains change.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
_cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
if _cors_env.strip():
    allowed_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
elif ENVIRONMENT == "production":
    allowed_origins = [
        "https://zumud.com",
        "https://www.zumud.com",
    ]
else:
    # In development, the local frontend dev server
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

logger.info(f"CORS allowed origins ({ENVIRONMENT}): {allowed_origins}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Content-Disposition"
    ],  # Expose Content-Disposition header to frontend
)

# # Create tables on startup
# @app.on_event("startup")
# async def startup_event():
#     create_tables()

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
        "redoc_url": "/redoc",
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
        "version": "1.0.0",
    }

    if not db_healthy:
        raise HTTPException(status_code=503, detail="Database connection failed")

    return health_status


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
