""""
Checkin Setting Model
"""
from __future__ import annotations

import enum
from datetime import datetime
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class FrequencyType(str, enum.Enum):
    DAILY = "daily"
    EVERY_N_DAYS = "every_n_days"

class CheckinReminder(Base, TimeStampMixin):
    reminder_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )

    enabled : Mapped[bool] = mapped_column(default=False)
    time_local: Mapped[str] = mapped_column(String(5), default="09:00")  # HH:MM format
    frequency_type: Mapped[FrequencyType] = mapped_column(default=FrequencyType.DAILY)
    interval_days: Mapped[int | None] = mapped_column(default=None)

    # relationship
    user: Mapped["User"] = relationship(back_populates="checkin_reminder")


class MissCheckinRule(Base, TimeStampMixin):
    rule_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )

    threshold_days : Mapped[int] = mapped_column(default=3)
    message_template: Mapped[str] = mapped_column(
        String(1000),
        default="Hi, {contact_name}, this is Lumenary. We haven't heard from {username} in {interval_days} days. "
                "Please consider reaching out to them to make sure they’re okay."
    )

    # relationship
    user: Mapped["User"] = relationship(back_populates="miss_checkin_rule")

class PauseStatus(Base, TimeStampMixin):
    pause_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True
    )

    paused: Mapped[bool] = mapped_column(default=False)
    paused_at: Mapped[datetime | None] = mapped_column(default=None)

    # relationship
    user: Mapped["User"] = relationship(back_populates="pause_status")