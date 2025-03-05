from fastapi import FastAPI
from backend.api.v1 import api_v1_router
from backend.models.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TailorMade API",
    description="API for TailorMade - AI-powered job application assistant",
    version="1.0.0"
)

# Include API version 1 router
app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the TailorMade API!",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
