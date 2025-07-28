"""Switch roles to Enum

Revision ID: 966bda9ed5d3
Revises: 9a3d7dcca56d
Create Date: 2025-07-28 14:57:28.500038

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "966bda9ed5d3"
down_revision: Union[str, None] = "9a3d7dcca56d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    role_enum = sa.Enum("ADMIN", "CURATOR", "VOLUNTEER", name="role_enum")
    role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "user",
        sa.Column(
            "role",
            role_enum,
            nullable=True,
        ),
    )

    op.execute("UPDATE \"user\" SET role = 'VOLUNTEER' WHERE role IS NULL")

    op.alter_column(
        "user",
        "role",
        nullable=False,
        server_default="VOLUNTEER",
    )

    op.drop_table("user_roles")
    op.drop_table("role")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("user", "role")
    op.execute("DROP TYPE IF EXISTS role_enum;")
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role")),
        sa.UniqueConstraint("name", name=op.f("uq_role_name")),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"], ["role.id"], name=op.f("fk_user_roles_role_id_role")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_user_roles_user_id_user")
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "role_id", name=op.f("pk_user_roles")
        ),
    )
