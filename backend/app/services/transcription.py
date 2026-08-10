from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from time import perf_counter
from typing import Any

import whisper

from app.core.config import settings


@dataclass(slots=True)
class TranscriptionSegmentResult:
    segment_index: int
    start_seconds: float
    end_seconds: float
    text: str
    average_log_probability: float | None
    no_speech_probability: float | None


@dataclass(slots=True)
class TranscriptionResult:
    text: str
    language: str | None
    model_name: str
    duration_seconds: float | None
    processing_seconds: float
    segments: list[TranscriptionSegmentResult]


@lru_cache(maxsize=1)
def get_whisper_model() -> Any:
    """Load and cache the Whisper model."""

    return whisper.load_model(
        settings.whisper_model_name,
        device=settings.whisper_device,
    )


def transcribe_audio(audio_path: Path) -> TranscriptionResult:
    """Transcribe one audio file using local Whisper."""

    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file does not exist: {audio_path}"
        )

    model = get_whisper_model()

    started_at = perf_counter()

    result = model.transcribe(
        str(audio_path),
        task="transcribe",
        fp16=False,
        verbose=False,
    )

    processing_seconds = perf_counter() - started_at

    raw_segments = result.get("segments", [])

    segments = [
        TranscriptionSegmentResult(
            segment_index=index,
            start_seconds=float(segment["start"]),
            end_seconds=float(segment["end"]),
            text=str(segment["text"]).strip(),
            average_log_probability=(
                float(segment["avg_logprob"])
                if segment.get("avg_logprob") is not None
                else None
            ),
            no_speech_probability=(
                float(segment["no_speech_prob"])
                if segment.get("no_speech_prob") is not None
                else None
            ),
        )
        for index, segment in enumerate(raw_segments)
    ]

    duration_seconds = (
        max(
            (segment.end_seconds for segment in segments),
            default=0.0,
        )
        or None
    )

    return TranscriptionResult(
        text=str(result.get("text", "")).strip(),
        language=result.get("language"),
        model_name=settings.whisper_model_name,
        duration_seconds=duration_seconds,
        processing_seconds=processing_seconds,
        segments=segments,
    )