"""
Warm Message Schema
"""
from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field, conlist, field_validator
from utils.constants import WarmMessageTags
from schemas.journals import JournalRecord


class WarmMessagesRequest(BaseModel):
    """
    Request body for POST /insights/warm-messages
    """
    text: str = Field(..., min_length=1, max_length=500, description="user journal")


class AIWarmMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    warm_message: str = Field(
        ...,
        max_length=200,
        description=(
            "One supportive sentence + a very short suggestion phrase. "
            "Example: 'That sounds meaningful. Take a moment to appreciate this.'"
        ),
    )
    tags: List[WarmMessageTags] = Field(default_factory=list)


class AIWarmMessageLists(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    message_id: uuid.UUID | None = Field(None, alias="group_id", serialization_alias="message_id")
    alternatives: List[AIWarmMessage] = Field(default_factory=list)

    generated_at: datetime | None = None


class JournalWithWarmMessage(JournalRecord):
    """
    allOf: JournalRecord + warm_message(nullable)
    """
    warm_message: AIWarmMessageLists | None = None


class ApiResponseJournalWithWarmMessage(BaseModel):
    data: JournalWithWarmMessage
    message: str = "OK"