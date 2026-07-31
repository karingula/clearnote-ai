from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.recording import RecordingStatus


class RecordingResponse(BaseModel):
    """Recording data returned through the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    status: RecordingStatus
    created_at: datetime


class RecordingListResponse(BaseModel):
    """Paginated list of recordings."""

    items: list[RecordingResponse]
    total: int
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class RecordingDeleteResponse(BaseModel):
    """Confirmation returned after deleting a recording."""

    id: UUID
    deleted: bool