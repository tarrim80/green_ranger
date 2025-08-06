"""Add thumbnails

Revision ID: cdf0e51a1ed3
Revises: 966bda9ed5d3
Create Date: 2025-08-06 10:06:25.265671

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cdf0e51a1ed3"
down_revision: Union[str, None] = "966bda9ed5d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "photo",
        sa.Column(
            "thumbnail_path",
            sa.String(length=255),
            nullable=False,
            comment="Путь к файлу миниатюры на сервере",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("photo", "thumbnail_path")
