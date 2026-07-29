from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services import audio_storage


client = TestClient(app)


def test_upload_audio_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        audio_storage,
        "AUDIO_STORAGE_DIRECTORY",
        tmp_path,
    )

    response = client.post(
        "/api/recordings",
        files={
            "file": (
                "sample.wav",
                b"fake audio content",
                "audio/wav",
            ),
        },
    )

    assert response.status_code == 201

    response_body = response.json()

    assert response_body["original_filename"] == "sample.wav"
    assert response_body["content_type"] == "audio/wav"
    assert response_body["size_bytes"] == len(b"fake audio content")
    assert response_body["status"] == "uploaded"

    stored_file = tmp_path / response_body["stored_filename"]

    assert stored_file.exists()
    assert stored_file.read_bytes() == b"fake audio content"


def test_reject_unsupported_file_type() -> None:
    response = client.post(
        "/api/recordings",
        files={
            "file": (
                "document.pdf",
                b"fake PDF content",
                "application/pdf",
            ),
        },
    )

    assert response.status_code == 415
    assert "Unsupported audio type" in response.json()["detail"]


def test_reject_empty_audio_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        audio_storage,
        "AUDIO_STORAGE_DIRECTORY",
        tmp_path,
    )

    response = client.post(
        "/api/recordings",
        files={
            "file": (
                "empty.wav",
                b"",
                "audio/wav",
            ),
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded audio file is empty."