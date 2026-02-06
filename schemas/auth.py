"""
Authentication Schemas
"""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, UUID4
from schemas.user import UserProfile


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, max_length=100)
    timezone: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

    device_name: Optional[str] = None
    device_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str
    session_id: UUID4

    model_config = ConfigDict(extra="forbid")


class TokenPair(BaseModel):
    """Token pair response"""
    access_token: str
    token_type: str = Field(default="Bearer", pattern="^Bearer$")
    expires_in: int

    refresh_token: str
    refresh_expires_in: int

    session_id: UUID4

    model_config = ConfigDict(extra="forbid")


class AuthResponse(TokenPair):
    """Authentication response with tokens and user"""
    user: UserProfile

    model_config = ConfigDict(extra="forbid")


class ApiResponseAuth(BaseModel):
    data: AuthResponse
    message: str = "OK"

    model_config = ConfigDict(extra="forbid")

class LogoutRequest(BaseModel):
    session_id: UUID4

    model_config = ConfigDict(extra="forbid")
