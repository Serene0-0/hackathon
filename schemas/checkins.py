import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict


class CheckinStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    checkin_id: uuid.UUID | None = None
    local_date: date
    checked_in_today: bool
    timezone_used: str | None = None

class ApiResponseCheckinStatus(BaseModel):
    data: CheckinStatus
    message: str = "OK"