from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import SurveyDefaults
from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.schemas.enums import SurveyStatusEnum, TreeConditionEnum

if TYPE_CHECKING:
    from app.models import Photo, Sector, SurveyDefect, User


class Survey(IntIdPkMixin, Base):
    """Модель обследования (осмотра) растения."""

    tree_id: Mapped[int] = mapped_column(
        ForeignKey("tree.id"),
        comment="ID растения",
    )
    age: Mapped[int | None] = mapped_column(comment="Возраст растения")
    height: Mapped[float | None] = mapped_column(
        comment="Высота растения в метрах"
    )
    diameter: Mapped[float | None] = mapped_column(
        comment="Диаметр ствола на высоте груди в см"
    )
    trunk_count: Mapped[int] = mapped_column(
        default=SurveyDefaults.TRUNK_COUNT,
        server_default=str(SurveyDefaults.TRUNK_COUNT),
        comment="Количество стволов",
    )
    condition: Mapped[TreeConditionEnum] = mapped_column(
        ENUM(TreeConditionEnum, name="tree_condition_enum"),
        default=SurveyDefaults.CONDITION,
        server_default=SurveyDefaults.CONDITION.name,
        comment="КСО",
    )
    is_emergency_report: Mapped[bool] = mapped_column(
        default=SurveyDefaults.IS_EMERGENCY_REPORT,
        server_default=str(SurveyDefaults.IS_EMERGENCY_REPORT),
        comment="Потенциально опасное",
    )
    note: Mapped[str | None] = mapped_column(Text(), comment="Примечание")
    survey_status: Mapped[SurveyStatusEnum] = mapped_column(
        ENUM(SurveyStatusEnum, name="survey_status_enum"),
        default=SurveyDefaults.SURVEY_STATUS,
        server_default=SurveyDefaults.SURVEY_STATUS.name,
        comment="Код статуса обследования",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID пользователя производящего обследование",
    )
    author: Mapped["User"] = relationship(
        "User",
        back_populates="created_surveys",
    )
    # TODO: Изменить на DateTime(timezone=True) и создать миграцию
    # для корректной работы с часовыми поясами.
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время проведения обследования",
    )
    # TODO: Изменить на DateTime(timezone=True) и создать миграцию
    # для корректной работы с часовыми поясами.
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время изменения данных (статуса)",
    )

    survey_defects: Mapped[list["SurveyDefect"]] = relationship(
        "SurveyDefect", back_populates="survey", cascade="all, delete-orphan"
    )
    tree_photos: Mapped[list["Photo"]] = relationship(
        "Photo",
        back_populates="tree_photo",
    )
