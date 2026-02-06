"""
Emergency Contact Model
"""
from __future__ import annotations

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class EmergencyContact(Base, TimeStampMixin):
    contact_id : Mapped[uuid.UUID] = mapped_column(
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

    name : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    contact_relationship: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # relationship
    user: Mapped["User"] = relationship(back_populates="emergency_contact")