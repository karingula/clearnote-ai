from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.recording import Recording, RecordingStatus
from app.schemas.recording import (
    RecordingDeleteResponse,
    RecordingListResponse,
    RecordingResponse,
)
from app.services import audio_storage


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
) -> Recording:
    """Validate, store and persist an uploaded audio recording."""

    extension = audio_storage.validate_audio_file(file)
    recording_id = uuid4()

    stored_filename, size_bytes = await audio_storage.save_audio_file(
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
    )

    try:
        session.add(recording)
        await session.commit()
        await session.refresh(recording)
    except SQLAlchemyError as exc:
        await session.rollback()

        stored_path = audio_storage.AUDIO_STORAGE_DIRECTORY() / stored_filename
        stored_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The recording metadata could not be saved.",
        ) from exc

    return recording


@router.get(
    "",
    response_model=RecordingListResponse,
)
async def list_recordings(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    session: AsyncSession = Depends(get_db_session),
) -> RecordingListResponse:
    """Return recordings ordered from newest to oldest."""

    total_result = await session.execute(
        select(func.count()).select_from(Recording)
    )
    total = total_result.scalar_one()

    recordings_result = await session.execute(
        select(Recording)
        .order_by(Recording.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    recordings = list(recordings_result.scalars().all())

    return RecordingListResponse(
        items=recordings,
        total=total,
        limit=limit,
        offset=offset,
    )


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


@router.delete(
    "/{recording_id}",
    response_model=RecordingDeleteResponse,
)
async def delete_recording(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> RecordingDeleteResponse:
    """Delete recording metadata and its locally stored audio file."""

    recording = await session.get(Recording, recording_id)

    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found.",
        )

    stored_path = (
        audio_storage.AUDIO_STORAGE_DIRECTORY / recording.stored_filename
    )

    try:
        await session.delete(recording)
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The recording could not be deleted.",
        ) from exc

    stored_path.unlink(missing_ok=True)

    return RecordingDeleteResponse(
        id=recording_id,
        deleted=True,
    )