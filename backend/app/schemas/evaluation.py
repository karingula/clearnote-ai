from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DecisionEvaluationResponse(BaseModel):
    matched_decisions: list[str]
    extra_ai_decisions: list[str]
    missed_reference_decisions: list[str]

    true_positives: int
    false_positives: int
    false_negatives: int

    precision: float
    recall: float
    f1: float


class EvaluationRunResponse(BaseModel):
    id: UUID

    generated_note_id: UUID
    reviewed_note_id: UUID

    evaluator_name: str
    evaluator_version: str

    predicted_decisions: list[str]
    reference_decisions: list[str]

    matched_decisions: list[str]
    extra_ai_decisions: list[str]
    missed_reference_decisions: list[str]

    true_positives: int
    false_positives: int
    false_negatives: int

    precision: float
    recall: float
    f1: float

    created_at: datetime


class EvaluationRunListResponse(BaseModel):
    items: list[EvaluationRunResponse]