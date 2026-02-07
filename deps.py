from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional

from db.session import get_db
from models.user import User
from ai.gemini_client import GeminiClient

DEMO_USER_ID = UUID("00000000-0000-0000-0000-000000000001")
_gemini_client: Optional[GeminiClient] = None

async def get_current_user_demo(db: AsyncSession = Depends(get_db)) -> User:
    user = (await db.execute(select(User).where(User.user_id == DEMO_USER_ID))).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo user not found in database"
        )
    return user

def get_gemini_client() -> GeminiClient:
    """
    Get a Gemini client
    only call at initialization
    """
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client