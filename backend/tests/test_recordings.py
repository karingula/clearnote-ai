from pathlib import Path
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.services import audio_storage


@pytest.mark.asyncio
async def test_upload_and_retrieve_recording(
    client: AsyncClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_storage,
        "AUDIO_STORAGE_DIRECTORY",
        tmp_path,
    )

    upload_response = await client.post(
        "/api/recordings",
        files={
            "file": (
                "sample.wav",
                b"fake audio content",
                "audio/wav",
            ),
        },
    )

    assert upload_response.status_code == 201

    uploaded = upload_response.json()
    recording_id = uploaded["id"]

    retrieve_response = await client.get(
        f"/api/recordings/{recording_id}"
    )

    assert retrieve_response.status_code == 200
    assert retrieve_response.json()["id"] == recording_id
    assert (
        retrieve_response.json()["original_filename"]
        == "sample.wav"
    )


@pytest.mark.asyncio
async def test_list_recordings(
    client: AsyncClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_storage,
        "AUDIO_STORAGE_DIRECTORY",
        tmp_path,
    )

    for filename in ["first.wav", "second.wav"]:
        response = await client.post(
            "/api/recordings",
            files={
                "file": (
                    filename,
                    b"fake audio content",
                    "audio/wav",
                ),
            },
        )

        assert response.status_code == 201

    list_response = await client.get(
        "/api/recordings?limit=20&offset=0"
    )

    assert list_response.status_code == 200

    body = list_response.json()

    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 20
    assert body["offset"] == 0


@pytest.mark.asyncio
async def test_delete_recording(
    client: AsyncClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        audio_storage,
        "AUDIO_STORAGE_DIRECTORY",
        tmp_path,
    )

    upload_response = await client.post(
        "/api/recordings",
        files={
            "file": (
                "sample.wav",
                b"fake audio content",
                "audio/wav",
            ),
        },
    )

    uploaded = upload_response.json()
    recording_id = uploaded["id"]
    stored_filename = uploaded["stored_filename"]

    stored_path = tmp_path / stored_filename

    assert stored_path.exists()

    delete_response = await client.delete(
        f"/api/recordings/{recording_id}"
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": recording_id,
        "deleted": True,
    }

    assert not stored_path.exists()

    retrieve_response = await client.get(
        f"/api/recordings/{recording_id}"
    )

    assert retrieve_response.status_code == 404


@pytest.mark.asyncio
async def test_unknown_recording_returns_404(
    client: AsyncClient,
) -> None:
    response = await client.get(
        f"/api/recordings/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Recording not found."


@pytest.mark.asyncio
async def test_reject_unsupported_file_type(
    client: AsyncClient,
) -> None:
    response = await client.post(
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