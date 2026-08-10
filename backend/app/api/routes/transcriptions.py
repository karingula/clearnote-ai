import asyncio
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.models.recording import Recording, RecordingStatus
from app.models.transcript import Transcript, TranscriptSegment
from app.schemas.transcript import TranscriptResponse
from app.services import audio_storage
from app.services.transcription import transcribe_audio


router = APIRouter(
    prefix="/api/recordings",
    tags=["Transcription"],
)


@router.post(
    "/{recording_id}/transcribe",
    response_model=TranscriptResponse,
)
async def transcribe_recording(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Transcript:
    recording = await session.get(Recording, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    existing_result = await session.execute(
        select(Transcript)
        .options(selectinload(Transcript.segments))
        .where(Transcript.recording_id == recording_id)
    )
    existing_transcript = existing_result.scalar_one_or_none()

    if existing_transcript is not None:
        return existing_transcript

    audio_path = (
        audio_storage.AUDIO_STORAGE_DIRECTORY
        / recording.stored_filename
    )

    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored audio file not found.",
        )

    recording.status = RecordingStatus.TRANSCRIBING
    recording.transcription_error = None
    recording.transcription_started_at = datetime.now(timezone.utc)

    await session.commit()

    try:
        result = await asyncio.to_thread(
            transcribe_audio,
            audio_path,
        )

        transcript = Transcript(
            recording_id=recording.id,
            text=result.text,
            language=result.language,
            model_name=result.model_name,
            duration_seconds=result.duration_seconds,
            processing_seconds=result.processing_seconds,
        )

        transcript.segments = [
            TranscriptSegment(
                segment_index=segment.segment_index,
                start_seconds=segment.start_seconds,
                end_seconds=segment.end_seconds,
                text=segment.text,
                average_log_probability=(
                    segment.average_log_probability
                ),
                no_speech_probability=(
                    segment.no_speech_probability
                ),
            )
            for segment in result.segments
        ]

        session.add(transcript)

        recording.status = RecordingStatus.TRANSCRIBED
        recording.transcription_completed_at = datetime.now(
            timezone.utc
        )

        await session.commit()

        transcript_result = await session.execute(
            select(Transcript)
            .options(selectinload(Transcript.segments))
            .where(Transcript.id == transcript.id)
        )

        return transcript_result.scalar_one()

    except Exception as exc:
        await session.rollback()

        recording = await session.get(Recording, recording_id)

        if recording is not None:
            recording.status = RecordingStatus.FAILED
            recording.transcription_error = str(exc)
            recording.transcription_completed_at = datetime.now(
                timezone.utc
            )

            try:
                await session.commit()
            except SQLAlchemyError:
                await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transcription failed.",
        ) from exc


@router.get(
    "/{recording_id}/transcript",
    response_model=TranscriptResponse,
)
async def get_transcript(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Transcript:
    result = await session.execute(
        select(Transcript)
        .options(selectinload(Transcript.segments))
        .where(Transcript.recording_id == recording_id)
    )

    transcript = result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found.",
        )

    return transcript