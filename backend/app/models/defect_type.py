from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from app.models import Photo, SurveyDefect


class DefectType(
    IntIdPkMixin,
    Base,
):
    """Модель видов дефектов (справочная)."""

    __verbose_name__ = "Вид дефекта"
    __verbose_name_plural__ = "Виды дефектов"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        comment="Наименование вида дефекта",
    )
    description: Mapped[str | None] = mapped_column(
        Text, comment="Общее описание вида дефекта"
    )
    images: Mapped[list["Photo"]] = relationship(
        "Photo", back_populates="defect_type_image"
    )
    survey_defects: Mapped[list["SurveyDefect"]] = relationship(
        "SurveyDefect", back_populates="defect_type"
    )
