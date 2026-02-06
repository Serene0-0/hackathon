from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class CheckinFrequencyType(str, Enum):
    daily = "daily"
    every_n_days = "every_n_days"


# -----------------------------
# /users/me/checkin-reminder
# -----------------------------
class CheckinReminder(BaseModel):
    """
    API schema for GET/PUT /users/me/checkin-reminder
    Mirrors DB: enabled, time_local, frequency_type, interval_days
    """
    model_config = ConfigDict(from_attributes=True)

    enabled: bool = Field(..., description="Whether check-in reminder is enabled")
    time_local: str = Field(..., description="HH:MM in user's local time (24-hour)", examples=["09:00"])
    frequency_type: CheckinFrequencyType = Field(..., description="Reminder frequency type")
    interval_days: Optional[int] = Field(
        None,
        ge=2,
        description="Required when frequency_type=every_n_days (>=2). Null when daily.",
        examples=[3],
    )

    @field_validator("time_local")
    @classmethod
    def validate_time_local(cls, v: str) -> str:
        # Strict HH:MM 24-hour
        if len(v) != 5 or v[2] != ":":
            raise ValueError("time_local must be in HH:MM format")
        hh, mm = v.split(":")
        if not (hh.isdigit() and mm.isdigit()):
            raise ValueError("time_local must be numeric HH:MM")
        h = int(hh)
        m = int(mm)
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError("time_local must be a valid 24-hour time")
        return v

    @field_validator("interval_days")
    @classmethod
    def validate_interval_days_with_frequency(cls, v: Optional[int], info):
        # Pydantic v2: cross-field validate via info.data
        freq = info.data.get("frequency_type")
        if freq == CheckinFrequencyType.every_n_days:
            if v is None:
                raise ValueError("interval_days is required when frequency_type=every_n_days")
            if v < 2:
                raise ValueError("interval_days must be >= 2 when frequency_type=every_n_days")
        else:
            # daily: interval_days should be null (keep strict to avoid confusing data)
            if v is not None:
                raise ValueError("interval_days must be null when frequency_type=daily")
        return v


class CheckinReminderUpdate(CheckinReminder):
    """
    Request body for PUT /users/me/checkin-reminder
    """
    pass


class ApiResponseCheckinReminder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: CheckinReminder
    message: str = "OK"


# -----------------------------
# /users/me/miss-checkin-rule
# -----------------------------
class MissCheckinRule(BaseModel):
    """
    API schema for GET/PUT /users/me/miss-checkin-rule
    Mirrors DB: threshold_days, message_template
    """
    model_config = ConfigDict(from_attributes=True)

    threshold_days: int = Field(..., ge=1, description="Trigger when consecutive natural days without check-in >= N")
    message_template: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Optional. If null/empty, backend will use default template."
    )


class MissCheckinRuleUpdate(MissCheckinRule):
    """
    Request body for PUT /users/me/miss-checkin-rule
    """
    pass


class ApiResponseMissCheckinRule(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: MissCheckinRule
    message: str = "OK"


# -----------------------------
# /users/me/pause-checkin
# -----------------------------
class PauseStatus(BaseModel):
    """
    Response schema for GET/POST /users/me/pause-checkin
    Mirrors DB: paused, paused_at
    """
    model_config = ConfigDict(from_attributes=True)

    paused: bool
    paused_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp when pause was enabled; null if not paused",
    )


class PauseStatusUpdate(BaseModel):
    """
    Request body for POST /users/me/pause-checkin
    """
    paused: bool


class ApiResponsePauseStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data: PauseStatus
    message: str = "OK"