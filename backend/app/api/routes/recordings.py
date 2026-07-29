from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, status

from app.models.recording import RecordingStatus
from app.schemas.recording import RecordingResponse
from app.services.audio_storage import save_audio_file, validate_audio_file


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
) -> RecordingResponse:
    """Validate and store an uploaded audio recording."""

    extension = validate_audio_file(file)
    recording_id = uuid4()

    stored_filename, size_bytes = await save_audio_file(
        file=file,
        recording_id=recording_id,
        extension=extension,
    )

    return RecordingResponse(
        id=recording_id,
        original_filename=file.filename or "unknown",
        stored_filename=stored_filename,
        content_type=file.content_type or "application/octet-stream",
        size_bytes=size_bytes,
        status=RecordingStatus.UPLOADED,
        created_at=datetime.now(timezone.utc),
    )