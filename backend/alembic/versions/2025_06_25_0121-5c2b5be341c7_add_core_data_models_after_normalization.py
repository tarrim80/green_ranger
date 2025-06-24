"""Add core data models after normalization

Revision ID: 5c2b5be341c7
Revises:
Create Date: 2025-06-25 01:21:36.501668

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5c2b5be341c7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "defect_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
            comment="Наименование вида дефекта",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
            comment="Общее описание вида дефекта",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_defect_type")),
        sa.UniqueConstraint("name", name=op.f("uq_defect_type_name")),
    )
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role")),
        sa.UniqueConstraint("name", name=op.f("uq_role_name")),
    )
    op.create_table(
        "team",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False,
            comment="Название команды",
        ),
        sa.Column(
            "leader_id",
            sa.Integer(),
            nullable=False,
            comment="ID лидера команды",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_team")),
        sa.UniqueConstraint("name", name=op.f("uq_team_name")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "telegram_id",
            sa.BigInteger(),
            nullable=False,
            comment="ID Telegram",
        ),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column(
            "firstname", sa.String(length=100), nullable=False, comment="Имя"
        ),
        sa.Column(
            "lastname",
            sa.String(length=100),
            nullable=False,
            comment="Фамилия",
        ),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["team_id"], ["team.id"], name=op.f("fk_user_team_id_team")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(
        op.f("ix_user_telegram_id"), "user", ["telegram_id"], unique=True
    )
    op.create_foreign_key(
        "fk_team_leader_id_user", "team", "user", ["leader_id"], ["id"]
    )

    op.create_geospatial_table(
        "sector",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False,
            comment="Название или номер участка",
        ),
        sa.Column(
            "curator_id",
            sa.Integer(),
            nullable=False,
            comment="ID куратора участка",
        ),
        sa.Column(
            "team_id",
            sa.Integer(),
            nullable=True,
            comment="ID команды, назначенной на участок",
        ),
        sa.Column(
            "color",
            sa.String(length=7),
            server_default="#000000",
            nullable=False,
            comment="Цвет для отображения участка на карте (HEX)",
        ),
        sa.Column(
            "geometry",
            Geometry(
                geometry_type="POLYGON",
                srid=4326,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
            comment="Геометрия (полигон) участка",
        ),
        sa.ForeignKeyConstraint(
            ["curator_id"], ["user.id"], name=op.f("fk_sector_curator_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["team_id"], ["team.id"], name=op.f("fk_sector_team_id_team")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sector")),
        sa.UniqueConstraint("name", name=op.f("uq_sector_name")),
    )
    op.create_geospatial_index(
        "idx_sector_geometry",
        "sector",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
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
    op.create_geospatial_table(
        "tree",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "planting",
            sa.String(length=50),
            nullable=False,
            comment="Вид насаждений",
        ),
        sa.Column(
            "species",
            sa.String(length=50),
            nullable=False,
            comment="Порода растения",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
            comment="Описание растения",
        ),
        sa.Column(
            "location",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
            comment="Местоположение растения",
        ),
        sa.Column(
            "azimuth",
            sa.Float(),
            nullable=True,
            comment="Азимут от точки привязки до растения",
        ),
        sa.Column(
            "distance",
            sa.Float(),
            nullable=True,
            comment="Расстояние от точки привязки до растения в метрах",
        ),
        sa.Column(
            "sector_id",
            sa.Integer(),
            nullable=False,
            comment="Учетный участок",
        ),
        sa.Column(
            "condition",
            postgresql.ENUM(
                "HEALTHY",
                "WEAKENED",
                "OPPRESSED",
                "DRYING",
                "DEAD",
                "REMOVED",
                name="tree_condition_enum",
            ),
            server_default="HEALTHY",
            nullable=False,
            comment="КСО",
        ),
        sa.Column(
            "is_emergency",
            sa.Boolean(),
            server_default="False",
            nullable=False,
            comment="Признак аварийности/срочности",
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            nullable=False,
            comment="ID автора регистрации растения",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата и время создания записи",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата и время изменения записи",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], name=op.f("fk_tree_author_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["sector_id"], ["sector.id"], name=op.f("fk_tree_sector_id_sector")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tree")),
    )
    op.create_geospatial_index(
        "idx_tree_location",
        "tree",
        ["location"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_table(
        "survey",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "tree_id", sa.Integer(), nullable=False, comment="ID растения"
        ),
        sa.Column(
            "age", sa.Integer(), nullable=True, comment="Возраст растения"
        ),
        sa.Column(
            "height",
            sa.Float(),
            nullable=True,
            comment="Высота растения в метрах",
        ),
        sa.Column(
            "diameter",
            sa.Float(),
            nullable=True,
            comment="Диаметр ствола на высоте груди в см",
        ),
        sa.Column(
            "trunk_count",
            sa.Integer(),
            server_default="1",
            nullable=False,
            comment="Количество стволов",
        ),
        sa.Column(
            "condition",
            postgresql.ENUM(
                "HEALTHY",
                "WEAKENED",
                "OPPRESSED",
                "DRYING",
                "DEAD",
                "REMOVED",
                name="tree_condition_enum",
            ),
            server_default="HEALTHY",
            nullable=False,
            comment="КСО",
        ),
        sa.Column(
            "is_emergency_report",
            sa.Boolean(),
            server_default="False",
            nullable=False,
            comment="Потенциально опасное",
        ),
        sa.Column("notes", sa.Text(), nullable=True, comment="Примечание"),
        sa.Column(
            "survey_status",
            postgresql.ENUM(
                "ON_REVIEW",
                "NEEDS_CORRECTION",
                "APPROVED",
                "REJECTED",
                name="survey_status_enum",
            ),
            server_default="ON_REVIEW",
            nullable=False,
            comment="Код статуса обследования",
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            nullable=False,
            comment="ID пользователя производящего обследование",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата и время проведения обследования",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата и время изменения данных (статуса)",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"], ["user.id"], name=op.f("fk_survey_author_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["tree_id"], ["tree.id"], name=op.f("fk_survey_tree_id_tree")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey")),
    )
    op.create_table(
        "survey_defect",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "survey_id",
            sa.Integer(),
            nullable=False,
            comment="ID обследования",
        ),
        sa.Column(
            "defect_type_id",
            sa.Integer(),
            nullable=False,
            comment="ID вида дефекта из справочника",
        ),
        sa.Column(
            "defect_status",
            postgresql.ENUM(
                "ACTIVE",
                "IN_PROCESSING",
                "RESOLVED",
                "NO_ACTION_NEEDED",
                "ON_MONITORING",
                name="defect_status_enum",
            ),
            server_default="ACTIVE",
            nullable=False,
            comment="Код статуса обработки этого дефекта",
        ),
        sa.Column(
            "description", sa.Text(), nullable=True, comment="Описание дефекта"
        ),
        sa.ForeignKeyConstraint(
            ["defect_type_id"],
            ["defect_type.id"],
            name=op.f("fk_survey_defect_defect_type_id_defect_type"),
        ),
        sa.ForeignKeyConstraint(
            ["survey_id"],
            ["survey.id"],
            name=op.f("fk_survey_defect_survey_id_survey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_defect")),
    )
    op.create_table(
        "photo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "file_path",
            sa.String(length=255),
            nullable=False,
            comment="Путь к файлу изображения на сервере",
        ),
        sa.Column(
            "uploaded_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата и время загрузки фото",
        ),
        sa.Column(
            "defect_type_id",
            sa.Integer(),
            nullable=True,
            comment="ID вида дефекта",
        ),
        sa.Column(
            "survey_id", sa.Integer(), nullable=True, comment="ID обследования"
        ),
        sa.Column(
            "survey_defect_id",
            sa.Integer(),
            nullable=True,
            comment="ID конкретного дефекта",
        ),
        sa.ForeignKeyConstraint(
            ["defect_type_id"],
            ["defect_type.id"],
            name=op.f("fk_photo_defect_type_id_defect_type"),
        ),
        sa.ForeignKeyConstraint(
            ["survey_defect_id"],
            ["survey_defect.id"],
            name=op.f("fk_photo_survey_defect_id_survey_defect"),
        ),
        sa.ForeignKeyConstraint(
            ["survey_id"],
            ["survey.id"],
            name=op.f("fk_photo_survey_id_survey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_photo")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("photo")
    op.drop_table("survey_defect")
    op.drop_table("survey")
    op.drop_geospatial_index(
        "idx_tree_location",
        table_name="tree",
        postgresql_using="gist",
        column_name="location",
    )
    op.drop_geospatial_table("tree")
    op.drop_table("user_roles")
    op.drop_geospatial_index(
        "idx_sector_geometry",
        table_name="sector",
        postgresql_using="gist",
        column_name="geometry",
    )
    op.drop_geospatial_table("sector")
    op.drop_index(op.f("ix_user_telegram_id"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_constraint("fk_team_leader_id_user", "team", type_="foreignkey")
    op.drop_table("user")
    op.drop_table("team")
    op.drop_table("role")
    op.drop_table("defect_type")
    op.execute("DROP TYPE IF EXISTS defect_status_enum;")
    op.execute("DROP TYPE IF EXISTS survey_status_enum;")
    op.execute("DROP TYPE IF EXISTS tree_condition_enum;")
