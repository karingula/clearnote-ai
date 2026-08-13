from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.recording import Recording
    from app.models.generated_note import GeneratedNote


class Transcript(Base):
    """Full transcription result for one recording."""

    __tablename__ = "transcripts"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    recording_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey(
            "recordings.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    model_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    processing_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    recording: Mapped["Recording"] = relationship(
        back_populates="transcript",
    )

    segments: Mapped[list["TranscriptSegment"]] = relationship(
        back_populates="transcript",
        cascade="all, delete-orphan",
        order_by="TranscriptSegment.segment_index",
    )

    generated_note: Mapped["GeneratedNote | None"] = relationship(
        back_populates="transcript",
        cascade="all, delete-orphan",
        uselist=False,
    )


class TranscriptSegment(Base):
    """Timestamped portion of a transcript."""

    __tablename__ = "transcript_segments"

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

    segment_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    start_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    end_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    average_log_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    no_speech_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    transcript: Mapped["Transcript"] = relationship(
        back_populates="segments",
    )