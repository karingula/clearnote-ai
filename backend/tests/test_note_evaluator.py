import json

from app.evaluation.note_evaluator import (
    evaluate_note_decisions,
)
from app.models.generated_note import GeneratedNote
from app.models.reviewed_note import ReviewedNote


def test_evaluate_note_decisions() -> None:
    generated_note = GeneratedNote(
        summary="AI summary",
        decisions_json=json.dumps(
            [
                "Deploy Monday",
                "Notify legal",
            ]
        ),
        action_items_json="[]",
        key_points_json="[]",
        follow_up_questions_json="[]",
        model_name="test-model",
        prompt_version="v1",
    )

    reviewed_note = ReviewedNote(
        summary="Human-reviewed summary",
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

    result = evaluate_note_decisions(
        generated_note,
        reviewed_note,
    )

    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1

    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5