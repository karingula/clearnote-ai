import json
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db_session
from app.evaluation.decision_evaluator import (
    EVALUATOR_NAME,
    EVALUATOR_VERSION,
)
from app.evaluation.note_evaluator import evaluate_note_decisions
from app.evaluation.dataset_evaluator import (
    evaluate_dataset,
)

from app.models.generated_note import GeneratedNote
from app.models.reviewed_note import ReviewedNote
from app.models.transcript import Transcript
from app.models.evaluation_run import EvaluationRun
from app.schemas.evaluation import (
    DecisionEvaluationResponse,
    EvaluationRunListResponse,
    EvaluationRunResponse,
    ExperimentEvaluationResponse,
    ExperimentComparisonResponse,
)


router = APIRouter(
    prefix="/api/recordings",
    tags=["Evaluation"],
)

@router.post(
    "/{recording_id}/evaluations",
    response_model=DecisionEvaluationResponse,
)
async def evaluate_recording(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session)
) -> DecisionEvaluationResponse:
    """Evaluate the decisions for a given recording by comparing the generated and reviewed notes."""
    transcript_result = await session.execute(
        select(Transcript).where(Transcript.recording_id == recording_id)
    )
    transcript = transcript_result.scalar_one_or_none()
    if transcript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not found")
    generated_note_result = await session.execute(
        select(GeneratedNote).where(GeneratedNote.transcript_id == transcript.id)
    )
    generated_note = generated_note_result.scalar_one_or_none()
    if generated_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated note not found")

    reviewed_note_result = await session.execute(
        select(ReviewedNote).where(ReviewedNote.generated_note_id == generated_note.id)
    )
    reviewed_note = reviewed_note_result.scalar_one_or_none()
    if reviewed_note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewed note not found")

    result = evaluate_note_decisions(
        generated_note=generated_note,
        reviewed_note=reviewed_note,
    )
    evaluation_run = EvaluationRun(
        generated_note_id=generated_note.id,
        reviewed_note_id=reviewed_note.id,
        evaluator_name=EVALUATOR_NAME,
        evaluator_version=EVALUATOR_VERSION,
        predicted_decisions_json=generated_note.decisions_json,
        reference_decisions_json=reviewed_note.decisions_json,
        matched_decisions_json=json.dumps(
            result["matched_decisions"]
        ),
        extra_ai_decisions_json=json.dumps(
            result["extra_ai_decisions"]
        ),
        missed_reference_decisions_json=json.dumps(
            result["missed_reference_decisions"]
        ),
        true_positives=result["true_positives"],
        false_positives=result["false_positives"],
        false_negatives=result["false_negatives"],
        precision=result["precision"],
        recall=result["recall"],
        f1=result["f1"],
    )
    session.add(evaluation_run)
    await session.commit()

    return DecisionEvaluationResponse(**result)

@router.get(
    "/{recording_id}/evaluations",
    response_model=EvaluationRunListResponse,
)
async def list_evaluation_runs(
    recording_id: UUID,
    session: AsyncSession = Depends(get_db_session),
) -> EvaluationRunListResponse:
    """Return saved evaluation runs for a recording."""

    transcript_result = await session.execute(
        select(Transcript).where(
            Transcript.recording_id == recording_id
        )
    )

    transcript = transcript_result.scalar_one_or_none()

    if transcript is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcript not found.",
        )

    generated_note_result = await session.execute(
        select(GeneratedNote).where(
            GeneratedNote.transcript_id == transcript.id
        )
    )

    generated_note = (
        generated_note_result.scalar_one_or_none()
    )

    if generated_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generated note not found.",
        )

    evaluation_result = await session.execute(
        select(EvaluationRun)
        .where(
            EvaluationRun.generated_note_id
            == generated_note.id
        )
        .order_by(
            EvaluationRun.created_at.desc()
        )
    )

    evaluation_runs = (
        evaluation_result.scalars().all()
    )

    items = [
        EvaluationRunResponse(
            id=run.id,
            generated_note_id=run.generated_note_id,
            reviewed_note_id=run.reviewed_note_id,
            evaluator_name=run.evaluator_name,
            evaluator_version=run.evaluator_version,
            model_name=generated_note.model_name,
            prompt_version=generated_note.prompt_version,

            predicted_decisions=json.loads(
                run.predicted_decisions_json
            ),
            reference_decisions=json.loads(
                run.reference_decisions_json
            ),

            matched_decisions=json.loads(
                run.matched_decisions_json
            ),
            extra_ai_decisions=json.loads(
                run.extra_ai_decisions_json
            ),
            missed_reference_decisions=json.loads(
                run.missed_reference_decisions_json
            ),

            true_positives=run.true_positives,
            false_positives=run.false_positives,
            false_negatives=run.false_negatives,

            precision=run.precision,
            recall=run.recall,
            f1=run.f1,

            created_at=run.created_at,
        )
        for run in evaluation_runs
    ]

    return EvaluationRunListResponse(
        items=items
    )

@router.get(
    "/dataset/evaluation",
    response_model=ExperimentEvaluationResponse,
)
async def evaluate_dataset_runs(
    model_name: str,
    prompt_version: str,
    evaluator_version: str,
    session: AsyncSession = Depends(get_db_session),
) -> ExperimentEvaluationResponse:
    """Aggregate evaluation runs for one experiment configuration."""

    evaluation_result = await session.execute(
        select(EvaluationRun)
        .join(
            GeneratedNote,
            EvaluationRun.generated_note_id
            == GeneratedNote.id,
        )
        .where(
            GeneratedNote.model_name == model_name,
            GeneratedNote.prompt_version == prompt_version,
            EvaluationRun.evaluator_version
            == evaluator_version,
        )
    )

    evaluation_runs = (
        evaluation_result.scalars().all()
    )

    results = [
        {
            "true_positives": run.true_positives,
            "false_positives": run.false_positives,
            "false_negatives": run.false_negatives,
        }
        for run in evaluation_runs
    ]

    result = evaluate_dataset(results)

    return ExperimentEvaluationResponse(
    model_name=model_name,
    prompt_version=prompt_version,
    evaluator_version=evaluator_version,
    **result,
)

@router.get(
    "/dataset/evaluation/compare",
    response_model=ExperimentComparisonResponse,
)
async def compare_experiments(
    model_name: str,
    prompt_version_a: str,
    prompt_version_b: str,
    evaluator_version: str,
    session: AsyncSession = Depends(get_db_session),
) -> ExperimentComparisonResponse:
    """Compare two prompt versions for the same model and evaluator."""

    async def get_experiment_result(
        prompt_version: str,
    ) -> ExperimentEvaluationResponse:
        evaluation_result = await session.execute(
            select(EvaluationRun)
            .join(
                GeneratedNote,
                EvaluationRun.generated_note_id
                == GeneratedNote.id,
            )
            .where(
                GeneratedNote.model_name == model_name,
                GeneratedNote.prompt_version
                == prompt_version,
                EvaluationRun.evaluator_version
                == evaluator_version,
            )
        )

        evaluation_runs = (
            evaluation_result.scalars().all()
        )

        results = [
            {
                "true_positives": run.true_positives,
                "false_positives": run.false_positives,
                "false_negatives": run.false_negatives,
            }
            for run in evaluation_runs
        ]

        result = evaluate_dataset(results)

        return ExperimentEvaluationResponse(
            model_name=model_name,
            prompt_version=prompt_version,
            evaluator_version=evaluator_version,
            **result,
        )

    experiment_a = await get_experiment_result(
        prompt_version_a
    )

    experiment_b = await get_experiment_result(
        prompt_version_b
    )

    return ExperimentComparisonResponse(
        experiment_a=experiment_a,
        experiment_b=experiment_b,
    )