import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class MoodCreateRequest(BaseModel):
    score: int = Field(..., ge=1, le=15)

class MoodRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mood_id: uuid.UUID
    local_date: date
    score: int
    occurred_at_utc: datetime
    timezone_used: str | None = None
    created_at: datetime

class MoodRecordList(BaseModel):
    items: list[MoodRecord]
    count: int

class ApiResponseMood(BaseModel):
    data: MoodRecord
    message: str = "OK"

class ApiResponseMoodList(BaseModel):
    data: MoodRecordList
    message: str = "OK"