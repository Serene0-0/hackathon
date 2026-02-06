from __future__ import annotations

from .auth import (UserRegister, UserLogin, RefreshTokenRequest,
                  TokenPair, AuthResponse, ApiResponseAuth, LogoutRequest)
from .common import ErrorDetail, ErrorResponse, MessageResponse
from .emergency_contact import EmergencyContact, EmergencyContactUpsert, ApiResponseEmergencyContact
from .user import UserProfile, UserProfileUpdate, ApiResponseUserProfile

__all__ = [
    # authentication
    "UserRegister",
    "UserLogin",
    "RefreshTokenRequest",
    "TokenPair",
    "AuthResponse",
    "ApiResponseAuth",

    # common
    "ErrorDetail",
    "ErrorResponse",
    "MessageResponse",

    # emergency contact
    "EmergencyContact",
    "EmergencyContactUpsert",
    "ApiResponseEmergencyContact",

    # user
    "UserProfile",
    "UserProfileUpdate",
    "ApiResponseUserProfile"

]