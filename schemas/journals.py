import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class JournalCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    title: str | None = Field(default=None, max_length=120)

class JournalRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    journal_id: uuid.UUID
    local_date: date
    title: str | None = None
    content: str
    occurred_at_utc: datetime
    timezone_used: str | None = None
    created_at: datetime

class JournalRecordList(BaseModel):
    items: list[JournalRecord]
    count: int
    next_cursor: str | None = None

class ApiResponseJournal(BaseModel):
    data: JournalRecord
    message: str = "OK"

class ApiResponseJournalList(BaseModel):
    data: JournalRecordList
    message: str = "OK"