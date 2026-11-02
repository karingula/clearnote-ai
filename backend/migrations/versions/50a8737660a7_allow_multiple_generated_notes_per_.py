"""allow multiple generated notes per transcript

Revision ID: 50a8737660a7
Revises: c787e3a0b4aa
Create Date: 2026-11-02 06:32:55.324301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50a8737660a7'
down_revision: Union[str, Sequence[str], None] = 'c787e3a0b4aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "generated_notes"
    ) as batch_op:
        batch_op.create_unique_constraint(
            "uq_generated_note_experiment",
            [
                "transcript_id",
                "model_name",
                "prompt_version",
            ],
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "generated_notes"
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_generated_note_experiment",
            type_="unique",
        )
