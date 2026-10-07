from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.generated_note import ActionItem


class ReviewedNoteContent(BaseModel):
    summary: str
    decisions: list[str]
    action_items: list[ActionItem]
    key_points: list[str]
    follow_up_questions: list[str]


class ReviewedNoteUpsertRequest(ReviewedNoteContent):
    pass


class ReviewedNoteResponse(ReviewedNoteContent):
    id: UUID
    generated_note_id: UUID
    reviewed_at: datetime
    updated_at: datetime