import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    generated_note_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "generated_notes.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    reviewed_note_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "reviewed_notes.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    evaluator_name: Mapped[str] = mapped_column(
        String(100),
    )

    evaluator_version: Mapped[str] = mapped_column(
        String(50),
    )

    predicted_decisions_json: Mapped[str] = mapped_column(
        Text,
    )

    reference_decisions_json: Mapped[str] = mapped_column(
        Text,
    )

    matched_decisions_json: Mapped[str] = mapped_column(
        Text,
    )

    extra_ai_decisions_json: Mapped[str] = mapped_column(
        Text,
    )

    missed_reference_decisions_json: Mapped[str] = mapped_column(
        Text,
    )

    true_positives: Mapped[int] = mapped_column(
        Integer,
    )

    false_positives: Mapped[int] = mapped_column(
        Integer,
    )

    false_negatives: Mapped[int] = mapped_column(
        Integer,
    )

    precision: Mapped[float] = mapped_column(
        Float,
    )

    recall: Mapped[float] = mapped_column(
        Float,
    )

    f1: Mapped[float] = mapped_column(
        Float,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )