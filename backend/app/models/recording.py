from datetime import datetime, timezone
from enum import StrEnum
from uuid import uuid4, UUID

from typing import TYPE_CHECKING


from sqlalchemy import BigInteger, String, Enum, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.transcript import Transcript

class RecordingStatus(StrEnum):
    """Possible processing states for an uploaded recording."""

    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    FAILED = "failed"

class Recording(Base):
    """Database model for an uploaded recording."""

    __tablename__ = "recordings"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4,)

    original_filename: Mapped[str] = mapped_column(String(255), nullable=False,)

    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True,)

    content_type: Mapped[str] = mapped_column(String(100), nullable=False,)

    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False,)

    status: Mapped[RecordingStatus] = mapped_column(
        Enum(RecordingStatus,
             name="recording_status_enum",
             values_callable=lambda enum_class: [item.value for item in RecordingStatus],
            ),
        nullable=False,
        default=RecordingStatus.UPLOADED,   
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    transcript: Mapped["Transcript | None"] = relationship(
    back_populates="recording",
    cascade="all, delete-orphan",
    uselist=False,
)