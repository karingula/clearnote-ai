import json

from app.evaluation.decision_evaluator import (
    evaluate_decisions,
)
from app.models.generated_note import GeneratedNote
from app.models.reviewed_note import ReviewedNote


def evaluate_note_decisions(
    generated_note: GeneratedNote,
    reviewed_note: ReviewedNote,
) -> dict[str, float | int]:
    """Evaluate AI-generated decisions against human-reviewed decisions."""

    predicted_decisions = json.loads(
        generated_note.decisions_json
    )

    reference_decisions = json.loads(
        reviewed_note.decisions_json
    )

    return evaluate_decisions(
        predicted=predicted_decisions,
        reference=reference_decisions,
    )