from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.recording import RecordingStatus


class RecordingResponse(BaseModel):
    """Information returned after an audio file is uploaded."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    status: RecordingStatus
    created_at: datetime