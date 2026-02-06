"""
Common Schemas
"""
from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ErrorDetail(BaseModel):
    """Error detail"""
    code: str = Field(..., examples=["VALIDATION_ERROR"])
    message: str = Field(..., examples=["Invalid input data"])
    details: Optional[dict[str, Any]] = None

    model_config = ConfigDict(extra="forbid")

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail
    timestamp: datetime

    model_config = ConfigDict(extra="forbid")


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str

    model_config = ConfigDict(extra="forbid")