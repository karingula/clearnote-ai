from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.recording import RecordingStatus, Recording
from app.schemas.recording import RecordingResponse
from app.services.audio_storage import (
    AUDIO_STORAGE_DIRECTORY,
    save_audio_file, validate_audio_file)


router = APIRouter(
    prefix="/api/recordings",
    tags=["Recordings"],
)


@router.post(
    "",
    response_model=RecordingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_recording(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> RecordingResponse:
    """Validate and store an uploaded audio recording."""

    extension = validate_audio_file(file)
    recording_id = uuid4()

    stored_filename, size_bytes = await save_audio_file(
        file=file,
        recording_id=recording_id,
        extension=extension,
    )

    recording = Recording(
        id=recording_id,
        original_filename=file.filename or "unknown",
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        status=RecordingStatus.UPLOADED,
        created_at=datetime.now(timezone.utc),
    )
    try:
        session.add(recording)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recording metadata: {str(e)}",
        )
    
    return recording


@router.get(
    "/{recording_id}",
    response_model=RecordingResponse,
)
async def get_recording(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Recording:
    """Retrieve a recording by its unique ID."""

    recording = await session.get(Recording, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    return recording