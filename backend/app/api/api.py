from fastapi import APIRouter
from app.api.routers import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
