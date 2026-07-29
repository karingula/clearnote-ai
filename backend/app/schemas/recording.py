from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.recording import RecordingStatus


class RecordingResponse(BaseModel):
    """Information returned after an audio file is uploaded."""

    id: UUID
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    status: RecordingStatus
    created_at: datetime