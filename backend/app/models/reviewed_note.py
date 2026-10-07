from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.generated_note import GeneratedNote


class ReviewedNote(Base):
    """Human-reviewed version of an AI-generated note."""

    __tablename__ = "reviewed_notes"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    generated_note_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "generated_notes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    decisions_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    action_items_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    key_points_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    follow_up_questions_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    generated_note: Mapped["GeneratedNote"] = relationship(
        "GeneratedNote",
        back_populates="reviewed_note",
    )