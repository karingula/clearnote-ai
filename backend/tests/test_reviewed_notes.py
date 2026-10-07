from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_note import GeneratedNote
from app.models.recording import (
    Recording,
    RecordingStatus,
)
from app.models.reviewed_note import ReviewedNote
from app.models.transcript import Transcript


async def create_recording(
    test_session: AsyncSession,
) -> Recording:
    """Create a recording for reviewed-note tests."""

    recording = Recording(
        original_filename="meeting.wav",
        stored_filename=f"{uuid4()}.wav",
        content_type="audio/wav",
        size_bytes=1024,
        status=RecordingStatus.TRANSCRIBED,
    )

    test_session.add(recording)

    await test_session.commit()
    await test_session.refresh(recording)

    return recording


async def create_transcript(
    test_session: AsyncSession,
    recording: Recording,
) -> Transcript:
    """Create a transcript for a recording."""

    transcript = Transcript(
        recording_id=recording.id,
        text=(
            "The team discussed deployment. "
            "They decided to deploy on Friday."
        ),
        language="en",
        model_name="tiny",
        duration_seconds=30.0,
        processing_seconds=2.0,
    )

    test_session.add(transcript)

    await test_session.commit()
    await test_session.refresh(transcript)

    return transcript


async def create_generated_note(
    test_session: AsyncSession,
    transcript: Transcript,
) -> GeneratedNote:
    """Create an AI-generated note for a transcript."""

    generated_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="The team discussed deployment.",
        decisions_json='["Deploy on Friday."]',
        action_items_json=(
            '[{"task": "Complete database migration.", '
            '"owner": "Vijay", '
            '"due_date": null}]'
        ),
        key_points_json='["API testing is complete."]',
        follow_up_questions_json="[]",
        model_name="gpt-5-mini",
        prompt_version="v1",
    )

    test_session.add(generated_note)

    await test_session.commit()
    await test_session.refresh(generated_note)

    return generated_note


async def create_generated_note_fixture(
    test_session: AsyncSession,
) -> tuple[
    Recording,
    Transcript,
    GeneratedNote,
]:
    """Create the full prerequisite chain for reviewed notes."""

    recording = await create_recording(
        test_session
    )

    transcript = await create_transcript(
        test_session,
        recording,
    )

    generated_note = await create_generated_note(
        test_session,
        transcript,
    )

    return (
        recording,
        transcript,
        generated_note,
    )


def reviewed_note_payload() -> dict:
    """Return a valid reviewed-note request payload."""

    return {
        "summary": (
            "The team finalized the deployment plan."
        ),
        "decisions": [
            "Deploy on Friday.",
        ],
        "action_items": [
            {
                "task": "Complete database migration.",
                "owner": "Vijay",
                "due_date": None,
            }
        ],
        "key_points": [
            "API testing is complete.",
        ],
        "follow_up_questions": [],
    }


@pytest.mark.asyncio
async def test_create_reviewed_notes(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording, _, generated_note = (
        await create_generated_note_fixture(
            test_session
        )
    )

    response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=reviewed_note_payload(),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["generated_note_id"] == str(
        generated_note.id
    )

    assert data["summary"] == (
        "The team finalized the deployment plan."
    )

    assert data["decisions"] == [
        "Deploy on Friday."
    ]

    assert data["action_items"] == [
        {
            "task": "Complete database migration.",
            "owner": "Vijay",
            "due_date": None,
        }
    ]

    assert data["key_points"] == [
        "API testing is complete."
    ]

    assert data["follow_up_questions"] == []

    assert data["id"] is not None
    assert data["reviewed_at"] is not None
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_update_existing_reviewed_notes(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording, _, _ = (
        await create_generated_note_fixture(
            test_session
        )
    )

    first_response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=reviewed_note_payload(),
    )

    assert first_response.status_code == 200

    first_data = first_response.json()
    first_id = first_data["id"]

    updated_payload = reviewed_note_payload()

    updated_payload["summary"] = (
        "The deployment plan was reviewed and approved."
    )

    updated_payload["decisions"] = [
        "Deploy on Monday instead of Friday."
    ]

    second_response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=updated_payload,
    )

    assert second_response.status_code == 200

    second_data = second_response.json()

    # This is the key upsert assertion.
    #
    # We expect the SAME ReviewedNote row to be
    # updated instead of another row being created.
    assert second_data["id"] == first_id

    assert second_data["summary"] == (
        "The deployment plan was reviewed and approved."
    )

    assert second_data["decisions"] == [
        "Deploy on Monday instead of Friday."
    ]

    result = await test_session.execute(
        select(
            func.count(ReviewedNote.id)
        )
    )

    reviewed_note_count = result.scalar_one()

    # There should still only be one reviewed note.
    assert reviewed_note_count == 1


@pytest.mark.asyncio
async def test_get_reviewed_notes(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording, _, _ = (
        await create_generated_note_fixture(
            test_session
        )
    )

    put_response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=reviewed_note_payload(),
    )

    assert put_response.status_code == 200

    created_data = put_response.json()

    response = await client.get(
        f"/api/recordings/{recording.id}/reviewed-notes"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == created_data["id"]

    assert data["summary"] == (
        "The team finalized the deployment plan."
    )

    assert data["decisions"] == [
        "Deploy on Friday."
    ]


@pytest.mark.asyncio
async def test_get_reviewed_notes_not_found(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording, _, _ = (
        await create_generated_note_fixture(
            test_session
        )
    )

    response = await client.get(
        f"/api/recordings/{recording.id}/reviewed-notes"
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Reviewed notes not found."
    )


@pytest.mark.asyncio
async def test_save_reviewed_notes_without_transcript(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = await create_recording(
        test_session
    )

    response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=reviewed_note_payload(),
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Transcript not found."
    )


@pytest.mark.asyncio
async def test_save_reviewed_notes_without_generated_note(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = await create_recording(
        test_session
    )

    await create_transcript(
        test_session,
        recording,
    )

    response = await client.put(
        f"/api/recordings/{recording.id}/reviewed-notes",
        json=reviewed_note_payload(),
    )

    assert response.status_code == 409

    assert response.json()["detail"] == (
        "Generated notes must exist before "
        "reviewed notes can be saved."
    )