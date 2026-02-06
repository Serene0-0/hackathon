"""
Emergency Contact Schema
"""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

class EmergencyContact(BaseModel):
    contact_id: uuid.UUID
    name: str
    email: EmailStr
    relationship: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class EmergencyContactUpsert(BaseModel):
    name: str
    email: EmailStr
    relationship: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class ApiResponseEmergencyContact(BaseModel):
    data: EmergencyContact
    message: str

    model_config = ConfigDict(extra="forbid")