"""move reviewed notes to transcript

Revision ID: f2ffa4c8d08d
Revises: 50a8737660a7
Create Date: 2026-11-08 10:18:11.990812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ffa4c8d08d'
down_revision: Union[str, Sequence[str], None] = '50a8737660a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Add transcript_id as nullable temporarily so existing rows
    # can survive while we backfill the value.
    op.add_column(
        "reviewed_notes",
        sa.Column(
            "transcript_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    # 2. Copy the transcript_id through the existing GeneratedNote.
    #
    # reviewed_note.generated_note_id
    #     -> generated_note.transcript_id
    op.execute(
        """
        UPDATE reviewed_notes
        SET transcript_id = (
            SELECT generated_notes.transcript_id
            FROM generated_notes
            WHERE generated_notes.id =
                  reviewed_notes.generated_note_id
        )
        """
    )

    # 3. Verify we did not leave any existing reviewed notes
    # without a transcript.
    connection = op.get_bind()

    missing_count = connection.execute(
        sa.text(
            """
            SELECT COUNT(*)
            FROM reviewed_notes
            WHERE transcript_id IS NULL
            """
        )
    ).scalar_one()

    if missing_count:
        raise RuntimeError(
            "Could not migrate all reviewed notes "
            "to transcript_id."
        )

    # 4. SQLite needs batch mode for this kind of table alteration.
    with op.batch_alter_table(
        "reviewed_notes"
    ) as batch_op:
        batch_op.drop_index(
            "ix_reviewed_notes_generated_note_id"
        )

        batch_op.alter_column(
            "transcript_id",
            existing_type=sa.Uuid(),
            nullable=False,
        )

        batch_op.create_index(
            "ix_reviewed_notes_transcript_id",
            ["transcript_id"],
            unique=True,
        )

        batch_op.create_foreign_key(
            "fk_reviewed_notes_transcript_id",
            "transcripts",
            ["transcript_id"],
            ["id"],
            ondelete="CASCADE",
        )

        batch_op.drop_column(
            "generated_note_id"
        )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade is not supported because canonical "
        "reviewed notes are now associated with transcripts, "
        "and a transcript may have multiple generated notes."
    )
