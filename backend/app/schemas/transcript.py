from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TranscriptSegmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    segment_index: int
    start_seconds: float
    end_seconds: float
    text: str
    average_log_probability: float | None
    no_speech_probability: float | None


class TranscriptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recording_id: UUID
    text: str
    language: str | None
    model_name: str
    duration_seconds: float | None
    processing_seconds: float | None
    created_at: datetime
    segments: list[TranscriptSegmentResponse]