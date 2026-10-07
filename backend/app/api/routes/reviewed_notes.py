import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.generated_note import GeneratedNote
from app.models.reviewed_note import ReviewedNote
from app.models.transcript import Transcript
from app.schemas.reviewed_note import (
    ReviewedNoteResponse,
    ReviewedNoteUpsertRequest,
)
from app.services.reviewed_notes import (
    reviewed_note_to_response,
)


router = APIRouter(
    prefix="/api/recordings",
    tags=["Reviewed Notes"],
)


@router.get(
    "/{recording_id}/reviewed-notes",
    response_model=ReviewedNoteResponse,
)
async def get_reviewed_notes(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> ReviewedNoteResponse:
    """Retrieve the human-reviewed notes for a recording."""

    transcript_result = await session.execute(
        select(Transcript).where(
            Transcript.recording_id == recording_id
        )
    )

    transcript = transcript_result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found.",
        )

    generated_note_result = await session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id == transcript.id
        )
    )

    generated_note = (
        generated_note_result.scalar_one_or_none()
    )

    if generated_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated notes not found.",
        )

    reviewed_note_result = await session.execute(
        select(ReviewedNote).where(
            ReviewedNote.generated_note_id
            == generated_note.id
        )
    )

    reviewed_note = (
        reviewed_note_result.scalar_one_or_none()
    )

    if reviewed_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reviewed notes not found.",
        )

    return reviewed_note_to_response(
        reviewed_note
    )


@router.put(
    "/{recording_id}/reviewed-notes",
    response_model=ReviewedNoteResponse,
)
async def upsert_reviewed_notes(
    recording_id: UUID,
    payload: ReviewedNoteUpsertRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ReviewedNoteResponse:
    """Create or update the human-reviewed notes for a recording."""

    transcript_result = await session.execute(
        select(Transcript).where(
            Transcript.recording_id == recording_id
        )
    )

    transcript = transcript_result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found.",
        )

    generated_note_result = await session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id == transcript.id
        )
    )

    generated_note = (
        generated_note_result.scalar_one_or_none()
    )

    if generated_note is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Generated notes must exist before "
                "reviewed notes can be saved."
            ),
        )

    reviewed_note_result = await session.execute(
        select(ReviewedNote).where(
            ReviewedNote.generated_note_id
            == generated_note.id
        )
    )

    reviewed_note = (
        reviewed_note_result.scalar_one_or_none()
    )

    try:
        if reviewed_note is None:
            reviewed_note = ReviewedNote(
                generated_note_id=generated_note.id,
                summary=payload.summary,
                decisions_json=json.dumps(
                    payload.decisions
                ),
                action_items_json=json.dumps(
                    [
                        item.model_dump(
                            mode="json"
                        )
                        for item in payload.action_items
                    ]
                ),
                key_points_json=json.dumps(
                    payload.key_points
                ),
                follow_up_questions_json=json.dumps(
                    payload.follow_up_questions
                ),
            )

            session.add(reviewed_note)

        else:
            reviewed_note.summary = (
                payload.summary
            )

            reviewed_note.decisions_json = (
                json.dumps(
                    payload.decisions
                )
            )

            reviewed_note.action_items_json = (
                json.dumps(
                    [
                        item.model_dump(
                            mode="json"
                        )
                        for item in payload.action_items
                    ]
                )
            )

            reviewed_note.key_points_json = (
                json.dumps(
                    payload.key_points
                )
            )

            reviewed_note.follow_up_questions_json = (
                json.dumps(
                    payload.follow_up_questions
                )
            )

            reviewed_note.updated_at = (
                datetime.now(timezone.utc)
            )

        await session.commit()
        await session.refresh(reviewed_note)

        return reviewed_note_to_response(
            reviewed_note
        )

    except SQLAlchemyError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Reviewed notes could not be saved.",
        ) from exc