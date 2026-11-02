from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.reviewed_note import ReviewedNote


if TYPE_CHECKING:
    from app.models.transcript import Transcript
    from app.models.reviewed_note import ReviewedNote


class GeneratedNote(Base):
    """Represents a Structured AI-generated notes associated with a transcript."""
    
    __tablename__ = "generated_notes"
    __table_args__ = (
        UniqueConstraint(
        "transcript_id",
        "model_name",
        "prompt_version",
        name="uq_generated_note_experiment",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    transcript_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "transcripts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
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

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    transcript: Mapped["Transcript"] = relationship(
        "Transcript",
        back_populates="generated_note",
    )

    reviewed_note: Mapped["ReviewedNote | None"] = relationship(
         "ReviewedNote",
         back_populates="generated_note",
         cascade="all, delete-orphan",
         uselist=False,
    )