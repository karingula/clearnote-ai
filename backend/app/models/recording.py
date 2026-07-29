from enum import StrEnum


class RecordingStatus(StrEnum):
    """Possible processing states for an uploaded recording."""

    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    FAILED = "failed"