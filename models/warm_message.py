"""
Warm Message Model
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, ForeignKey, Table, Column, UniqueConstraint, ForeignKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from typing import List
from sqlalchemy import Enum as SAEnum

from db import Base, TimeStampMixin
from utils.constants import WarmMessageTags


warm_msg_tags = Table(
    "warm_msg_tags",
    Base.metadata,
    Column("message_id", PG_UUID(as_uuid=True),
           ForeignKey("warm_messages.message_id", ondelete="CASCADE"),
           primary_key=True),
    Column("tag", SAEnum(WarmMessageTags, name="warm_tag"), primary_key=True),
)


class WarmMessageGroup(Base, TimeStampMixin):
    group_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default = uuid.uuid4
    )
    journal_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("journals.journal_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    generated_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    alternatives : Mapped[List["WarmMessage"]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
    )

    # relationship
    journal: Mapped["Journal"] = relationship(
        back_populates="warm_message_group"
    )

    __table_args__ = (
        UniqueConstraint("group_id", "journal_id", name="uq_warm_message_groups_group_id_journal_id"),
    )


class WarmMessage(Base, TimeStampMixin):
    message_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default = uuid.uuid4
    )
    journal_id : Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("journals.journal_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    group_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True
    )

    content : Mapped[str] = mapped_column(String(200))

    # relationship
    group : Mapped["WarmMessageGroup"] = relationship(
        back_populates="alternatives"
    )


    __table_args__ = (
        ForeignKeyConstraint(
            ["group_id", "journal_id"],
            ["warm_message_groups.group_id", "warm_message_groups.journal_id"],
            ondelete="CASCADE"
        ),
    )
