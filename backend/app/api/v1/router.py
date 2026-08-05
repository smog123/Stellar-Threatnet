from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, threats

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(threats.router)
api_router.include_router(admin.router)
