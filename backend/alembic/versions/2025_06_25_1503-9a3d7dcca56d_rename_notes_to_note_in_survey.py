"""Rename notes to note in survey

Revision ID: 9a3d7dcca56d
Revises: 5c2b5be341c7
Create Date: 2025-06-25 15:03:18.021145

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9a3d7dcca56d"
down_revision: Union[str, None] = "5c2b5be341c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "survey",
        sa.Column("note", sa.Text(), nullable=True, comment="Примечание"),
    )
    op.drop_column("survey", "notes")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "survey",
        sa.Column(
            "notes",
            sa.TEXT(),
            autoincrement=False,
            nullable=True,
            comment="Примечание",
        ),
    )
    op.drop_column("survey", "note")
