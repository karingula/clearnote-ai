import json

from app.models.generated_note import GeneratedNote
from app.schemas.generated_note import (
    ActionItem,
    GeneratedNoteResponse,
)


def to_generated_note_response(
    note: GeneratedNote,
) -> GeneratedNoteResponse:
    """Convert database JSON strings into API response objects."""

    return GeneratedNoteResponse(
        id=note.id,
        transcript_id=note.transcript_id,
        summary=note.summary,
        decisions=json.loads(note.decisions_json),
        action_items=[
            ActionItem.model_validate(item)
            for item in json.loads(note.action_items_json)
        ],
        key_points=json.loads(note.key_points_json),
        follow_up_questions=json.loads(
            note.follow_up_questions_json
        ),
        model_name=note.model_name,
        prompt_version=note.prompt_version,
        created_at=note.created_at,
    )