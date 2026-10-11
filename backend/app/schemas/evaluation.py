from pydantic import BaseModel

class DecisionEvaluationResponse(BaseModel):
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float

