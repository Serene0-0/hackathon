from __future__ import annotations

import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class MissCheckinAlertLog(Base, TimeStampMixin):
    """
    Record that we have already alerted for a specific 'absence window'
    keyed by (user_id, last_checkin_date).
    """
    alert_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    last_checkin_date: Mapped[date] = mapped_column(Date, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "last_checkin_date", name="uq_miss_checkin_alert_once"),
    )
