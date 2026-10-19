import re

def normalize_text(value: str) -> str:
    """Normalize text so simple formatting differences do not matter."""
    value = value.lower()
    value = re.sub(r"[^\w\s]", "", value)
    value = " ".join(value.split())
    return value


def evaluate_decisions(
    predicted: list[str],
    reference: list[str],
) -> dict:
    """Evaluate predicted decisions against human-reviewed decisions."""

    predicted_by_normalized = {
        normalize_text(item): item
        for item in predicted
    }

    reference_by_normalized = {
        normalize_text(item): item
        for item in reference
    }

    predicted_normalized = set(
        predicted_by_normalized.keys()
    )

    reference_normalized = set(
        reference_by_normalized.keys()
    )

    matched_normalized = (
        predicted_normalized
        & reference_normalized
    )

    extra_normalized = (
        predicted_normalized
        - reference_normalized
    )

    missed_normalized = (
        reference_normalized
        - predicted_normalized
    )

    matched_decisions = [
        predicted_by_normalized[item]
        for item in matched_normalized
    ]

    extra_ai_decisions = [
        predicted_by_normalized[item]
        for item in extra_normalized
    ]

    missed_reference_decisions = [
        reference_by_normalized[item]
        for item in missed_normalized
    ]

    true_positives = len(matched_decisions)
    false_positives = len(extra_ai_decisions)
    false_negatives = len(
        missed_reference_decisions
    )

    precision = (
        true_positives
        / (true_positives + false_positives)
        if true_positives + false_positives > 0
        else 0.0
    )

    recall = (
        true_positives
        / (true_positives + false_negatives)
        if true_positives + false_negatives > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "matched_decisions": matched_decisions,
        "extra_ai_decisions": extra_ai_decisions,
        "missed_reference_decisions":
            missed_reference_decisions,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }