from fastapi import APIRouter
from backend.api.v1.auth import router as auth_router
from backend.api.v1.users import router as users_router
from backend.api.v1.applications import router as applications_router

api_v1_router = APIRouter(prefix="/api/v1") 
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(applications_router)
