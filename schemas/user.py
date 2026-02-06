"""
User Schemas
"""
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from datetime import datetime


class UserProfile(BaseModel):
    """User profile response"""
    user_id: uuid.UUID
    email: str
    username: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    created_at: datetime
    avatar_url: Optional[HttpUrl] = None

    # future-ready (nullable)
    last_login_at: Optional[datetime] = None
    active_devices_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    username: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None  # set null to remove

    model_config = ConfigDict(extra="forbid")

class ApiResponseUserProfile(BaseModel):
    data: UserProfile
    message: str = "OK"

    model_config = ConfigDict(extra="forbid")