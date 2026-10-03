from fastapi import APIRouter
from app.api.routers import auth, transactions, webhook

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentification"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["finances"])
api_router.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
