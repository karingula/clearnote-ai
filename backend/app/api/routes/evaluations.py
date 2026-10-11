from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db_session
from app.evaluation.note_evaluator import evaluate_note_decisions

from app.models.generated_note import GeneratedNote
from app.models.reviewed_note import ReviewedNote
from app.models.transcript import Transcript
from app.schemas.evaluation import DecisionEvaluationResponse

router = APIRouter(
    prefix="/api/recordings",
    tags=["Evaluation"],
)
@router.get("/{recording_id}/evaluation", response_model=DecisionEvaluationResponse)
async def evaluate_recording(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> DecisionEvaluationResponse:
    """Evaluate the decisions for a given recording by comparing the generated and reviewed notes."""
    transcript_result = await session.execute(
        select(Transcript).where(Transcript.recording_id == recording_id)
    )
    transcript = transcript_result.scalar_one_or_none()
    if transcript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    generated_note_result = await session.execute(
        select(GeneratedNote).where(GeneratedNote.transcript_id == transcript.id)
    )
    generated_note = generated_note_result.scalar_one_or_none()
    if generated_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated note not found")

    reviewed_note_result = await session.execute(
        select(ReviewedNote).where(ReviewedNote.generated_note_id == generated_note.id)
    )
    reviewed_note = reviewed_note_result.scalar_one_or_none()
    if reviewed_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewed note not found")

    result = evaluate_note_decisions(
        generated_note=generated_note,
        reviewed_note=reviewed_note,
    )

    return DecisionEvaluationResponse(**result)