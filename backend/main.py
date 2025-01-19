from fastapi import FastAPI
from backend.api.endpoints import func_router
from backend.api.auth import auth_router
from backend.database.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TailorMade Backend", version="1.0.0")
app.include_router(func_router, prefix="/func", tags=["functions"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the TailorMade API!"}
