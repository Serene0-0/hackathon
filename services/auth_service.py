"""
Authentication Service
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import logging

from models.user import User
from models.refresh_token import RefreshToken
from schemas.auth import UserRegister, UserLogin, RefreshTokenRequest
from schemas.user import UserProfile
from core.security import hash_password, verify_password, create_access_token
from core.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """
    Authentication service logic
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> Dict:
        """
        Register a new user
        :param user_data: user data from request
        :return: dictionary with user data and tokens
        :raises: HTTPException 409: User already exists(email already exists)
        """

        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        # check if user email exists
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
