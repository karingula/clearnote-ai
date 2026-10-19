import json

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evaluation_run import EvaluationRun
from app.models.generated_note import GeneratedNote
from app.models.recording import Recording
from app.models.reviewed_note import ReviewedNote
from app.models.transcript import Transcript


@pytest.mark.asyncio
async def test_create_evaluation_run(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = Recording(
        original_filename="test.wav",
        stored_filename="test.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="Deploy Monday and notify customers.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    generated_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="Test summary",
        decisions_json=json.dumps(
            [
                "Deploy Monday",
                "Notify legal",
            ]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    test_session.add(generated_note)
    await test_session.flush()

    reviewed_note = ReviewedNote(
        generated_note_id=generated_note.id,
        summary="Reviewed summary",
        decisions_json=json.dumps(
            [
                "Deploy Monday",
                "Notify customers",
            ]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(reviewed_note)
    await test_session.commit()

    response = await client.post(
        f"/api/recordings/{recording.id}/evaluations"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["true_positives"] == 1
    assert body["false_positives"] == 1
    assert body["false_negatives"] == 1

    assert body["precision"] == pytest.approx(0.5)
    assert body["recall"] == pytest.approx(0.5)
    assert body["f1"] == pytest.approx(0.5)

    assert body["matched_decisions"] == [
        "Deploy Monday"
    ]

    assert body["extra_ai_decisions"] == [
        "Notify legal"
    ]

    assert body["missed_reference_decisions"] == [
        "Notify customers"
    ]

    result = await test_session.execute(
        select(EvaluationRun).where(
            EvaluationRun.generated_note_id
            == generated_note.id
        )
    )

    evaluation_run = result.scalar_one_or_none()

    assert evaluation_run is not None

    assert evaluation_run.evaluator_name == (
        "decision_evaluator"
    )

    assert evaluation_run.evaluator_version == "v1"

    assert json.loads(
        evaluation_run.predicted_decisions_json
    ) == [
        "Deploy Monday",
        "Notify legal",
    ]

    assert json.loads(
        evaluation_run.reference_decisions_json
    ) == [
        "Deploy Monday",
        "Notify customers",
    ]

    assert evaluation_run.true_positives == 1
    assert evaluation_run.false_positives == 1
    assert evaluation_run.false_negatives == 1
    assert evaluation_run.precision == pytest.approx(0.5)
    assert evaluation_run.recall == pytest.approx(0.5)
    assert evaluation_run.f1 == pytest.approx(0.5)


@pytest.mark.asyncio
async def test_list_evaluation_runs(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = Recording(
        original_filename="history.wav",
        stored_filename="history.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="Deploy Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    generated_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="Test summary",
        decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    test_session.add(generated_note)
    await test_session.flush()

    reviewed_note = ReviewedNote(
        generated_note_id=generated_note.id,
        summary="Reviewed summary",
        decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(reviewed_note)
    await test_session.flush()

    evaluation_run = EvaluationRun(
        generated_note_id=generated_note.id,
        reviewed_note_id=reviewed_note.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        reference_decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        matched_decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=1,
        false_positives=0,
        false_negatives=0,
        precision=1.0,
        recall=1.0,
        f1=1.0,
    )

    test_session.add(evaluation_run)
    await test_session.commit()

    response = await client.get(
        f"/api/recordings/{recording.id}/evaluations"
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["items"]) == 1

    item = body["items"][0]

    assert item["evaluator_name"] == (
        "decision_evaluator"
    )

    assert item["evaluator_version"] == "v1"

    assert item["predicted_decisions"] == [
        "Deploy Monday"
    ]

    assert item["reference_decisions"] == [
        "Deploy Monday"
    ]

    assert item["matched_decisions"] == [
        "Deploy Monday"
    ]

    assert item["extra_ai_decisions"] == []
    assert item["missed_reference_decisions"] == []

    assert item["true_positives"] == 1
    assert item["false_positives"] == 0
    assert item["false_negatives"] == 0
    assert item["precision"] == pytest.approx(1.0)
    assert item["recall"] == pytest.approx(1.0)
    assert item["f1"] == pytest.approx(1.0)

@pytest.mark.asyncio
async def test_create_evaluation_run_without_transcript_returns_404(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = Recording(
        original_filename="no-transcript.wav",
        stored_filename="no-transcript.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="uploaded",
    )

    test_session.add(recording)
    await test_session.commit()

    response = await client.post(
        f"/api/recordings/{recording.id}/evaluations"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transcript not found"


@pytest.mark.asyncio
async def test_create_evaluation_run_without_generated_note_returns_404(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = Recording(
        original_filename="no-note.wav",
        stored_filename="no-note.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="Deploy Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.commit()

    response = await client.post(
        f"/api/recordings/{recording.id}/evaluations"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Generated note not found"


@pytest.mark.asyncio
async def test_create_evaluation_run_without_reviewed_note_returns_404(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    recording = Recording(
        original_filename="no-review.wav",
        stored_filename="no-review.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="Deploy Monday.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    generated_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="Test summary",
        decisions_json=json.dumps(
            ["Deploy Monday"]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    test_session.add(generated_note)
    await test_session.commit()

    response = await client.post(
        f"/api/recordings/{recording.id}/evaluations"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Reviewed note not found"