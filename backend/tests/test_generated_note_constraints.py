import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_note import GeneratedNote
from app.models.recording import Recording
from app.models.transcript import Transcript


@pytest.mark.asyncio
async def test_same_transcript_allows_different_prompt_versions(
    test_session: AsyncSession,
) -> None:
    """
    One transcript should be allowed to have multiple generated notes
    when the experiment configuration is different.
    """

    recording = Recording(
        original_filename="meeting.wav",
        stored_filename="meeting.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="We agreed to deploy on Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    note_v1 = GeneratedNote(
        transcript_id=transcript.id,
        summary="Summary from prompt v1",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    note_v2 = GeneratedNote(
        transcript_id=transcript.id,
        summary="Summary from prompt v2",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v2",
    )

    test_session.add_all([
        note_v1,
        note_v2,
    ])

    await test_session.flush()

    # Both rows should have been successfully created.
    assert note_v1.id is not None
    assert note_v2.id is not None

    # Same transcript...
    assert note_v1.transcript_id == note_v2.transcript_id

    # ...but different prompt versions.
    assert note_v1.prompt_version == "v1"
    assert note_v2.prompt_version == "v2"


@pytest.mark.asyncio
async def test_same_transcript_rejects_duplicate_experiment_configuration(
    test_session: AsyncSession,
) -> None:
    """
    The same transcript + model + prompt version combination
    should not be allowed twice.
    """

    recording = Recording(
        original_filename="duplicate-meeting.wav",
        stored_filename="duplicate-meeting.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="We agreed to deploy on Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    first_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="First note",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    duplicate_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="Duplicate note",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    test_session.add(first_note)
    await test_session.flush()

    test_session.add(duplicate_note)

    with pytest.raises(IntegrityError):
        await test_session.flush()

    # After a database integrity failure,
    # SQLAlchemy requires us to roll the transaction back.
    await test_session.rollback()