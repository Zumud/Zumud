from fastapi import FastAPI
from backend.api.endpoints import func_router
from backend.api.auth import auth_router
from backend.api.users import user_router
from backend.models.db import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TailorMade Backend", version="1.0.0")
app.include_router(func_router)
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the TailorMade API!"}
