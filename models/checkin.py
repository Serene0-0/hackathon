""""
Checkin Record Model
"""
from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class CheckinRecord(Base, TimeStampMixin):
    checkin_id : Mapped[uuid.UUID] = mapped_column(
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

    local_date : Mapped[datetime] = mapped_column(default=datetime.utcnow())
    timezone_used: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        default = None
    )


    __table_args__ = (
        UniqueConstraint('user_id', 'local_date', name='uq_user_local_date_checkin'),
    )
