from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

########################### What this service does: ##################################################
# This service is responsible for validating and storing uploaded audio files. 
# Rejects missing filenames
# Rejects unsupported content types
# Creates a unique stored filename
# Reads the upload in 1 MB chunks
# Rejects files above 25 MB
# Deletes incomplete files when something fails
# Rejects empty files
######################################################################################################



AUDIO_STORAGE_DIRECTORY = Path("storage/audio")

MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/webm": ".webm",
}


def validate_audio_file(file: UploadFile) -> str:
    """
    Validate the uploaded file's declared content type.

    Returns the expected extension when the file is accepted.
    """

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must have a filename.",
        )

    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must include a content type.",
        )

    extension = ALLOWED_AUDIO_TYPES.get(file.content_type)

    if extension is None:
        allowed_types = ", ".join(sorted(ALLOWED_AUDIO_TYPES))

        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported audio type: {file.content_type}. "
                f"Allowed types: {allowed_types}."
            ),
        )

    return extension


async def save_audio_file(
    file: UploadFile,
    recording_id: UUID,
    extension: str,
) -> tuple[str, int]:
    """
    Save an uploaded audio file in chunks.

    Returns:
        A tuple containing the stored filename and total file size.
    """

    AUDIO_STORAGE_DIRECTORY.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{recording_id}{extension}"
    destination = AUDIO_STORAGE_DIRECTORY / stored_filename

    total_size = 0
    chunk_size = 1024 * 1024  # 1 MB

    try:
        with destination.open("wb") as output_file:
            while chunk := await file.read(chunk_size):
                total_size += len(chunk)

                if total_size > MAX_AUDIO_SIZE_BYTES:
                    output_file.close()
                    destination.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Audio files cannot exceed 25 MB.",
                    )

                output_file.write(chunk)
    except HTTPException:
        raise
    except OSError as exc:
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The audio file could not be stored.",
        ) from exc
    finally:
        await file.close()

    if total_size == 0:
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded audio file is empty.",
        )

    return stored_filename, total_size