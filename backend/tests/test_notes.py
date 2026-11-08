import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.generated_note import GeneratedNote

from app.schemas.generated_note import (
    ActionItem,
    GeneratedNoteContent,
)
from app.models.recording import Recording
from app.models.transcript import Transcript

@pytest.mark.asyncio
async def test_generate_notes(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def mock_generate_note_content(
        transcript_text: str,
    ) -> GeneratedNoteContent:
        return GeneratedNoteContent(
            summary="The team discussed deployment.",
            decisions=["Deploy on Friday."],
            action_items=[
                ActionItem(
                    task="Complete database migration.",
                    owner="Vijay",
                    due_date=None,
                )
            ],
            key_points=["API testing is complete."],
            follow_up_questions=[],
        )

    monkeypatch.setattr(
        "app.api.routes.notes.generate_note_content",
        mock_generate_note_content,
    )

    # Next: create a recording + transcript in the test DB,
    # then call POST /api/recordings/{id}/generate-notes
    
@pytest.mark.asyncio
async def test_generate_notes_allows_multiple_prompt_versions(
    client,
    test_session,
) -> None:
    recording = Recording(
        original_filename="experiment.wav",
        stored_filename="experiment.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="The team agreed to deploy on Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.commit()

    response_v1 = await client.post(
        f"/api/recordings/{recording.id}/generate-notes",
        params={
            "prompt_version": "v1",
        },
    )

    response_v2 = await client.post(
        f"/api/recordings/{recording.id}/generate-notes",
        params={
            "prompt_version": "v2",
        },
    )

    assert response_v1.status_code == 200
    assert response_v2.status_code == 200

    body_v1 = response_v1.json()
    body_v2 = response_v2.json()

    assert body_v1["prompt_version"] == "v1"
    assert body_v2["prompt_version"] == "v2"

    assert body_v1["model_name"] == body_v2["model_name"]

    assert body_v1["id"] != body_v2["id"]

    result = await test_session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id
            == transcript.id
        )
    )

    notes = result.scalars().all()

    assert len(notes) == 2

    assert {
        note.prompt_version
        for note in notes
    } == {
        "v1",
        "v2",
    }