"""
Mood Record Model
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class Mood(Base, TimeStampMixin):
    mood_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default = uuid.uuid4
    )
    user_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    score : Mapped[int] = mapped_column()
    local_date : Mapped[date] = mapped_column()

    occurred_at_utc  : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    timezone_used :Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default = None
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'local_date', name='uq_user_local_date_mood'),
    )