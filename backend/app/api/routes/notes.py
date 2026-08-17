import json
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

from app.core.config import settings
from app.core.database import get_db_session
from app.models.generated_note import GeneratedNote
from app.models.recording import Recording
from app.models.transcript import Transcript
from app.schemas.generated_note import GeneratedNoteResponse
from app.services.ai_notes import (
    PROMPT_VERSION,
    generate_note_content,
)
from app.services.generated_notes import (
    to_generated_note_response,
)


router = APIRouter(
    prefix="/api/recordings",
    tags=["AI Notes"],
)


@router.post(
    "/{recording_id}/generate-notes",
    response_model=GeneratedNoteResponse,
)
async def generate_notes(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> GeneratedNoteResponse:
    """Generate structured AI notes for a recording transcript."""

    recording = await session.get(Recording, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    transcript_result = await session.execute(
        select(Transcript).where(
            Transcript.recording_id == recording_id
        )
    )
    transcript = transcript_result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The recording must be transcribed "
                "before notes can be generated."
            ),
        )

    existing_result = await session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id == transcript.id
        )
    )
    existing_note = existing_result.scalar_one_or_none()

    if existing_note is not None:
        return to_generated_note_response(existing_note)

    try:
        content = await generate_note_content(
            transcript.text
        )

        generated_note = GeneratedNote(
            transcript_id=transcript.id,
            summary=content.summary,
            decisions_json=json.dumps(
                content.decisions
            ),
            action_items_json=json.dumps(
                [
                    item.model_dump(
                        mode="json"
                    )
                    for item in content.action_items
                ]
            ),
            key_points_json=json.dumps(
                content.key_points
            ),
            follow_up_questions_json=json.dumps(
                content.follow_up_questions
            ),
            model_name=settings.openai_model,
            prompt_version=PROMPT_VERSION,
        )

        session.add(generated_note)

        await session.commit()
        await session.refresh(generated_note)

        return to_generated_note_response(
            generated_note
        )

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Generated notes could not be saved.",
        ) from exc

    except Exception as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI note generation failed.",
        ) from exc


@router.get(
    "/{recording_id}/notes",
    response_model=GeneratedNoteResponse,
)
async def get_notes(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> GeneratedNoteResponse:
    """Retrieve generated notes for a recording."""

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

    note_result = await session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id == transcript.id
        )
    )

    note = note_result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated notes not found.",
        )

    return to_generated_note_response(note)