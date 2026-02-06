from fastapi import APIRouter

from .safety import router as safety_router

api_router = APIRouter()
api_router.include_router(safety_router, tags=["Safety"])

__all__ = ["api_router"]