import pytest

from app.evaluation.decision_evaluator import (
    evaluate_decisions,
    normalize_text,
)


def test_normalize_text() -> None:
    result = normalize_text(
        "  Deploy MONDAY!!!  "
    )

    assert result == "deploy monday"


def test_all_decisions_match() -> None:
    result = evaluate_decisions(
        predicted=[
            "Deploy Monday",
            "Notify customers",
        ],
        reference=[
            "Deploy Monday",
            "Notify customers",
        ],
    )

    assert result["true_positives"] == 2
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0

    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_some_decisions_match() -> None:
    result = evaluate_decisions(
        predicted=[
            "Deploy Monday.",
            "Run migration first",
            "Notify legal",
        ],
        reference=[
            "Deploy Monday",
            "Run migration first",
            "Notify customers",
        ],
    )

    assert result["true_positives"] == 2
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1

    assert result["precision"] == pytest.approx(
        2 / 3
    )

    assert result["recall"] == pytest.approx(
        2 / 3
    )

    assert result["f1"] == pytest.approx(
        2 / 3
    )


def test_ai_invents_decisions() -> None:
    result = evaluate_decisions(
        predicted=[
            "Deploy Monday",
            "Notify legal",
        ],
        reference=[
            "Deploy Monday",
        ],
    )

    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 0

    assert result["precision"] == 0.5
    assert result["recall"] == 1.0
    assert result["f1"] == pytest.approx(
        2 * (0.5 * 1.0) / (0.5 + 1.0)
    )


def test_ai_misses_decisions() -> None:
    result = evaluate_decisions(
        predicted=[
            "Deploy Monday",
        ],
        reference=[
            "Deploy Monday",
            "Notify customers",
        ],
    )

    assert result["true_positives"] == 1
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 1

    assert result["precision"] == 1.0
    assert result["recall"] == 0.5


def test_no_predictions() -> None:
    result = evaluate_decisions(
        predicted=[],
        reference=[
            "Deploy Monday",
        ],
    )

    assert result["true_positives"] == 0
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 1

    assert result["precision"] == 0.0
    assert result["recall"] == 0.0
    assert result["f1"] == 0.0