import re

def normalize_text(value: str) -> str:
    """Normalize text so that the simple formatting differences do not matter."""

    value = value.lower()
    value = re.sub(r"[^\w\s]", "", value)
    value = ' '.join(value.split())
    return value

def evaluate_decisions(predicted: list[str], reference: list[str]) -> dict[str, float | int]:
    """Evaluate the predicted decisions against the reference decisions."""
    predicted_normalized = [normalize_text(p) for p in predicted]
    reference_normalized = [normalize_text(r) for r in reference]

    true_positives = len(set(predicted_normalized) & set(reference_normalized))
    false_positives = len(set(predicted_normalized) - set(reference_normalized))
    false_negatives = len(set(reference_normalized) - set(predicted_normalized))

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }