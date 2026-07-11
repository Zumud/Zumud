from fastapi import APIRouter

from backend.api.applications import router as applications_router
from backend.api.auth import router as auth_router
from backend.api.billing import router as billing_router
from backend.api.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(applications_router)
api_router.include_router(billing_router)
