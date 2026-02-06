""""
User Model
"""
from __future__ import annotations

from datetime import datetime
import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from db import Base, TimeStampMixin

class User(Base, TimeStampMixin):
    """
    User account model
    Table name auto-generated: users
    """
    # primary key
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # Profile
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="momo",
        server_default="momo"
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(1024),
        nullable=True,
        comment="Public avatar URL (CDN / signed URL if applicable)"
    )
    avatar_storage_key: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Object storage key/path for avatar (e.g., s3 key)"
    )
    avatar_etag: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="Avatar version hash/etag for cache busting"
    )
    avatar_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last time avatar was updated"
    )


    # Timezone
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="UTC",
        nullable=False,
        comment="User timezone preference (IANA identifier)"
    )

    last_known_timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Last detected timezone from X-User-Timezone header"
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

    emergency_contact: Mapped["EmergencyContact | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    checkin_reminder: Mapped["CheckinReminder | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    miss_checkin_rule: Mapped["MissCheckinRule | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    pause_status: Mapped["PauseStatus | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )



    def __repr__(self):
        return f"<User(id={self.user_id}, email={self.email})>"
