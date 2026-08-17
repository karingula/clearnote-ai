import pytest
from httpx import AsyncClient

from app.schemas.generated_note import (
    ActionItem,
    GeneratedNoteContent,
)


@pytest.mark.asyncio
async def test_generate_notes(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def mock_generate_note_content(
        transcript_text: str,
    ) -> GeneratedNoteContent:
        return GeneratedNoteContent(
            summary="The team discussed deployment.",
            decisions=["Deploy on Friday."],
            action_items=[
                ActionItem(
                    task="Complete database migration.",
                    owner="Vijay",
                    due_date=None,
                )
            ],
            key_points=["API testing is complete."],
            follow_up_questions=[],
        )

    monkeypatch.setattr(
        "app.api.routes.notes.generate_note_content",
        mock_generate_note_content,
    )

    # Next: create a recording + transcript in the test DB,
    # then call POST /api/recordings/{id}/generate-notes