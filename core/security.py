"""
Security Utilities: JWT and Password Hashing
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt algorithm.
    :param password: password input by user
    :return: hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    :return: boolean: Ture if password is correct; else return False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create JWT access token.
    :param data: payload (must include user_id as UUID or string)
    :return: encoded JWT access token
    """
    to_encode = data.copy()

    # Convert UUID to string for JWT
    if "user_id" in to_encode and isinstance(to_encode["user_id"], uuid.UUID):
        to_encode["user_id"] = str(to_encode["user_id"])

    # Set expiry
    expire = datetime.now(timezone.utc) + timedelta(
        seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )

    # Add JWT claims
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    # Encode
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify JWT access token.
    :param token: JWT access token
    :return: decoded payload
    :raises: JWTError: if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")