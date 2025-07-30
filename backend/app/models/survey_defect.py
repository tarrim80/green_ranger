from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.schemas.defaults import SurveyDefectDefaults
from app.schemas.enums import DefectStatusEnum

if TYPE_CHECKING:
    from app.models import DefectType, Photo, Survey


class SurveyDefect(
    IntIdPkMixin,
    Base,
):
    """Модель конкретного дефекта, обнаруженного при обследовании."""

    __verbose_name__ = "Дефект"
    __verbose_name_plural__ = "Дефекты"

    # TODO: (Требует миграции) Добавить в индексы (index=True)
    survey_id: Mapped[int] = mapped_column(
        ForeignKey("survey.id"), comment="ID обследования"
    )
    survey: Mapped["Survey"] = relationship(
        "Survey",
        back_populates="survey_defects",
    )
    # TODO: (Требует миграции) Добавить в индексы (index=True)
    defect_type_id: Mapped[int] = mapped_column(
        ForeignKey("defect_type.id"),
        comment="ID вида дефекта из справочника",
    )
    defect_type: Mapped["DefectType"] = relationship(
        "DefectType",
        back_populates="survey_defects",
    )
    defect_status: Mapped[DefectStatusEnum] = mapped_column(
        ENUM(
            DefectStatusEnum,
            name="defect_status_enum",
        ),
        default=SurveyDefectDefaults.DEFECT_STATUS,
        server_default=SurveyDefectDefaults.DEFECT_STATUS.name,
        comment="Код статуса обработки этого дефекта",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        comment="Описание дефекта",
    )

    photos: Mapped[list["Photo"]] = relationship(
        "Photo",
        back_populates="survey_defect_photo",
    )
