from fastapi import APIRouter

from .safety import router as safety_router
from .moods import router as moods_router
from .journals import router as journals_router
from .checkins import router as checkins_router

api_router = APIRouter()
api_router.include_router(safety_router, tags=["Safety"])
api_router.include_router(moods_router, tags=["Moods"])
api_router.include_router(journals_router, tags=["Journals"])
api_router.include_router(checkins_router, tags=["Checkins"])

__all__ = ["api_router"]