import pytest

from app.evaluation.dataset_evaluator import (
    evaluate_dataset,
)


def test_evaluate_dataset() -> None:
    results = [
        {
            "true_positives": 2,
            "false_positives": 1,
            "false_negatives": 1,
        },
        {
            "true_positives": 3,
            "false_positives": 0,
            "false_negatives": 1,
        },
        {
            "true_positives": 1,
            "false_positives": 2,
            "false_negatives": 0,
        },
    ]

    result = evaluate_dataset(results)

    assert result["example_count"] == 3

    assert result["true_positives"] == 6
    assert result["false_positives"] == 3
    assert result["false_negatives"] == 2

    assert result["precision"] == pytest.approx(
        6 / 9
    )

    assert result["recall"] == pytest.approx(
        6 / 8
    )

    expected_f1 = (
        2
        * (6 / 9)
        * (6 / 8)
        / ((6 / 9) + (6 / 8))
    )

    assert result["f1"] == pytest.approx(
        expected_f1
    )

def test_evaluate_empty_dataset() -> None:
    result = evaluate_dataset([])

    assert result["example_count"] == 0
    assert result["true_positives"] == 0
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0