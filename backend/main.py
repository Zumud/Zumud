from fastapi import FastAPI
from backend.api.endpoints import router

app = FastAPI(title="TailorMade Backend", version="1.0.0")
app.include_router(router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the TailorMade API!"}
