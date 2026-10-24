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

@pytest.mark.asyncio
async def test_dataset_evaluation(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    # ---------------------------------------------------------
    # FIRST RECORDING
    # This one uses:
    # model = mock-model
    # prompt = v1
    # ---------------------------------------------------------

    recording = Recording(
        original_filename="dataset.wav",
        stored_filename="dataset.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording)
    await test_session.flush()

    transcript = Transcript(
        recording_id=recording.id,
        text="Test transcript.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript)
    await test_session.flush()

    generated_note = GeneratedNote(
        transcript_id=transcript.id,
        summary="Test summary",
        decisions_json="[]",
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
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(reviewed_note)
    await test_session.flush()

    # First v1 evaluation run
    run_1 = EvaluationRun(
        generated_note_id=generated_note.id,
        reviewed_note_id=reviewed_note.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=2,
        false_positives=1,
        false_negatives=1,
        precision=2 / 3,
        recall=2 / 3,
        f1=2 / 3,
    )

    # Second v1 evaluation run
    run_2 = EvaluationRun(
        generated_note_id=generated_note.id,
        reviewed_note_id=reviewed_note.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=3,
        false_positives=0,
        false_negatives=1,
        precision=1.0,
        recall=0.75,
        f1=0.857142857,
    )

    # ---------------------------------------------------------
    # SECOND RECORDING
    # This one uses prompt v2.
    #
    # We want to prove that it gets EXCLUDED when we ask
    # the API specifically for prompt_version=v1.
    # ---------------------------------------------------------

    second_recording = Recording(
        original_filename="dataset-v2.wav",
        stored_filename="dataset-v2.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(second_recording)
    await test_session.flush()

    second_transcript = Transcript(
        recording_id=second_recording.id,
        text="Another test transcript.",
        model_name="whisper-tiny",
    )

    test_session.add(second_transcript)
    await test_session.flush()

    second_generated_note = GeneratedNote(
        transcript_id=second_transcript.id,
        summary="Another summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",

        # IMPORTANT:
        # This is v2, not v1.
        prompt_version="v2",
    )

    test_session.add(second_generated_note)
    await test_session.flush()

    second_reviewed_note = ReviewedNote(
        generated_note_id=second_generated_note.id,
        summary="Another reviewed summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(second_reviewed_note)
    await test_session.flush()

    # This run intentionally has a huge TP value.
    #
    # If our filtering is broken, this 100 will appear
    # in the dataset result.
    #
    # If filtering works, this entire run will be ignored.
    run_v2 = EvaluationRun(
        generated_note_id=second_generated_note.id,
        reviewed_note_id=second_reviewed_note.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=100,
        false_positives=0,
        false_negatives=0,
        precision=1.0,
        recall=1.0,
        f1=1.0,
    )

    # Save all three evaluation runs.
    test_session.add_all([
        run_1,
        run_2,
        run_v2,
    ])

    await test_session.commit()

    # ---------------------------------------------------------
    # Ask specifically for:
    #
    # model = mock-model
    # prompt = v1
    # evaluator = v1
    #
    # Therefore run_v2 should NOT be included.
    # ---------------------------------------------------------

    response = await client.get(
        "/api/recordings/dataset/evaluation",
        params={
            "model_name": "mock-model",
            "prompt_version": "v1",
            "evaluator_version": "v1",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["model_name"] == "mock-model"
    assert body["prompt_version"] == "v1"
    assert body["evaluator_version"] == "v1"

    # Only run_1 and run_2 should be counted.
    assert body["example_count"] == 2

    # run_1 TP = 2
    # run_2 TP = 3
    #
    # Total = 5
    #
    # If run_v2 were accidentally included,
    # this would become 105.
    assert body["true_positives"] == 5

    # run_1 FP = 1
    # run_2 FP = 0
    assert body["false_positives"] == 1

    # run_1 FN = 1
    # run_2 FN = 1
    assert body["false_negatives"] == 2

    assert body["precision"] == pytest.approx(
        5 / 6
    )

    assert body["recall"] == pytest.approx(
        5 / 7
    )

@pytest.mark.asyncio
async def test_compare_experiments(
    client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    # ---------------------------------------------------------
    # EXPERIMENT A
    # model = mock-model
    # prompt = v1
    # evaluator = v1
    # ---------------------------------------------------------

    recording_a = Recording(
        original_filename="compare-v1.wav",
        stored_filename="compare-v1.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording_a)
    await test_session.flush()

    transcript_a = Transcript(
        recording_id=recording_a.id,
        text="Prompt v1 transcript.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript_a)
    await test_session.flush()

    generated_note_a = GeneratedNote(
        transcript_id=transcript_a.id,
        summary="Prompt v1 summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v1",
    )

    test_session.add(generated_note_a)
    await test_session.flush()

    reviewed_note_a = ReviewedNote(
        generated_note_id=generated_note_a.id,
        summary="Reviewed v1 summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(reviewed_note_a)
    await test_session.flush()

    run_a_1 = EvaluationRun(
        generated_note_id=generated_note_a.id,
        reviewed_note_id=reviewed_note_a.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=2,
        false_positives=2,
        false_negatives=1,
        precision=0.5,
        recall=2 / 3,
        f1=0.571428571,
    )

    run_a_2 = EvaluationRun(
        generated_note_id=generated_note_a.id,
        reviewed_note_id=reviewed_note_a.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=2,
        false_positives=1,
        false_negatives=1,
        precision=2 / 3,
        recall=2 / 3,
        f1=2 / 3,
    )

    # ---------------------------------------------------------
    # EXPERIMENT B
    # same model
    # same evaluator
    # different prompt = v2
    # ---------------------------------------------------------

    recording_b = Recording(
        original_filename="compare-v2.wav",
        stored_filename="compare-v2.wav",
        content_type="audio/wav",
        size_bytes=100,
        status="transcribed",
    )

    test_session.add(recording_b)
    await test_session.flush()

    transcript_b = Transcript(
        recording_id=recording_b.id,
        text="Prompt v2 transcript.",
        model_name="whisper-tiny",
    )

    test_session.add(transcript_b)
    await test_session.flush()

    generated_note_b = GeneratedNote(
        transcript_id=transcript_b.id,
        summary="Prompt v2 summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="mock-model",
        prompt_version="v2",
    )

    test_session.add(generated_note_b)
    await test_session.flush()

    reviewed_note_b = ReviewedNote(
        generated_note_id=generated_note_b.id,
        summary="Reviewed v2 summary",
        decisions_json="[]",
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
    )

    test_session.add(reviewed_note_b)
    await test_session.flush()

    run_b_1 = EvaluationRun(
        generated_note_id=generated_note_b.id,
        reviewed_note_id=reviewed_note_b.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=4,
        false_positives=0,
        false_negatives=1,
        precision=1.0,
        recall=0.8,
        f1=0.888888889,
    )

    run_b_2 = EvaluationRun(
        generated_note_id=generated_note_b.id,
        reviewed_note_id=reviewed_note_b.id,
        evaluator_name="decision_evaluator",
        evaluator_version="v1",
        predicted_decisions_json="[]",
        reference_decisions_json="[]",
        matched_decisions_json="[]",
        extra_ai_decisions_json="[]",
        missed_reference_decisions_json="[]",
        true_positives=3,
        false_positives=0,
        false_negatives=0,
        precision=1.0,
        recall=1.0,
        f1=1.0,
    )

    test_session.add_all([
        run_a_1,
        run_a_2,
        run_b_1,
        run_b_2,
    ])

    await test_session.commit()

    # ---------------------------------------------------------
    # Compare v1 vs v2
    # ---------------------------------------------------------

    response = await client.get(
        "/api/recordings/dataset/evaluation/compare",
        params={
            "model_name": "mock-model",
            "prompt_version_a": "v1",
            "prompt_version_b": "v2",
            "evaluator_version": "v1",
        },
    )

    assert response.status_code == 200

    body = response.json()

    experiment_a = body["experiment_a"]
    experiment_b = body["experiment_b"]

    # ---------------------------------------------------------
    # Verify experiment A identity
    # ---------------------------------------------------------

    assert experiment_a["model_name"] == "mock-model"
    assert experiment_a["prompt_version"] == "v1"
    assert experiment_a["evaluator_version"] == "v1"

    # v1 totals:
    # TP = 2 + 2 = 4
    # FP = 2 + 1 = 3
    # FN = 1 + 1 = 2

    assert experiment_a["example_count"] == 2
    assert experiment_a["true_positives"] == 4
    assert experiment_a["false_positives"] == 3
    assert experiment_a["false_negatives"] == 2

    assert experiment_a["precision"] == pytest.approx(
        4 / 7
    )

    assert experiment_a["recall"] == pytest.approx(
        4 / 6
    )

    # ---------------------------------------------------------
    # Verify experiment B identity
    # ---------------------------------------------------------

    assert experiment_b["model_name"] == "mock-model"
    assert experiment_b["prompt_version"] == "v2"
    assert experiment_b["evaluator_version"] == "v1"

    # v2 totals:
    # TP = 4 + 3 = 7
    # FP = 0 + 0 = 0
    # FN = 1 + 0 = 1

    assert experiment_b["example_count"] == 2
    assert experiment_b["true_positives"] == 7
    assert experiment_b["false_positives"] == 0
    assert experiment_b["false_negatives"] == 1

    assert experiment_b["precision"] == pytest.approx(
        1.0
    )

    assert experiment_b["recall"] == pytest.approx(
        7 / 8
    )

    # v2 should perform better than v1
    assert experiment_b["f1"] > experiment_a["f1"]