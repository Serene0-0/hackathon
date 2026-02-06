"""
Journal Record Model
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, String, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class Journal(Base, TimeStampMixin):
    journal_id : Mapped[uuid.UUID] = mapped_column(
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
    local_date: Mapped[date] = mapped_column(nullable=False)

    title: Mapped[str | None] = mapped_column(String(120), default=None)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    occurred_at_utc  : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    timezone_used: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        default=None
    )

    warm_message_group: Mapped["WarmMessageGroup"] = relationship(
        back_populates="journal",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )