import json

from app.models.reviewed_note import ReviewedNote
from app.schemas.generated_note import ActionItem
from app.schemas.reviewed_note import ReviewedNoteResponse


def reviewed_note_to_response(
    reviewed_note: ReviewedNote,
) -> ReviewedNoteResponse:
    return ReviewedNoteResponse(
        id=reviewed_note.id,
        generated_note_id=reviewed_note.generated_note_id,
        summary=reviewed_note.summary,
        decisions=json.loads(
            reviewed_note.decisions_json
        ),
        action_items=[
            ActionItem(**item)
            for item in json.loads(
                reviewed_note.action_items_json
            )
        ],
        key_points=json.loads(
            reviewed_note.key_points_json
        ),
        follow_up_questions=json.loads(
            reviewed_note.follow_up_questions_json
        ),
        reviewed_at=reviewed_note.reviewed_at,
        updated_at=reviewed_note.updated_at,
    )