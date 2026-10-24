def evaluate_dataset(
    evaluation_results: list[dict],
) -> dict[str, float | int]:
    """Aggregate decision evaluation results across many examples."""

    total_true_positives = sum(
        result["true_positives"]
        for result in evaluation_results
    )

    total_false_positives = sum(
        result["false_positives"]
        for result in evaluation_results
    )

    total_false_negatives = sum(
        result["false_negatives"]
        for result in evaluation_results
    )

    precision = (
        total_true_positives
        / (
            total_true_positives
            + total_false_positives
        )
        if (
            total_true_positives
            + total_false_positives
        ) > 0
        else 0.0
    )

    recall = (
        total_true_positives
        / (
            total_true_positives
            + total_false_negatives
        )
        if (
            total_true_positives
            + total_false_negatives
        ) > 0
        else 0.0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "example_count": len(evaluation_results),
        "true_positives": total_true_positives,
        "false_positives": total_false_positives,
        "false_negatives": total_false_negatives,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }