from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from app.models import DefectType, Survey, SurveyDefect


class Photo(
    IntIdPkMixin,
    Base,
):
    """Модель фотографий"""

    __verbose_name__ = "Фото"
    __verbose_name_plural__ = "Фото"

    file_path: Mapped[str] = mapped_column(
        String(255),
        comment="Путь к файлу изображения на сервере",
    )
    # TODO: (Требует миграции) Изменить на DateTime(timezone=True) и создать миграцию
    # для корректной работы с часовыми поясами.
    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время загрузки фото",
    )
    # TODO: (Требует миграции) Добавить в индексы (index=True)
    defect_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("defect_type.id"),
        comment="ID вида дефекта",
    )
    defect_type_image: Mapped["DefectType"] = relationship(
        "DefectType", back_populates="images"
    )
    # TODO: (Требует миграции) Добавить в индексы (index=True)
    survey_id: Mapped[int | None] = mapped_column(
        ForeignKey("survey.id"),
        comment="ID обследования",
    )
    tree_photo: Mapped["Survey"] = relationship(
        "Survey", back_populates="tree_photos"
    )
    # TODO: (Требует миграции) Добавить в индексы (index=True)
    survey_defect_id: Mapped[int | None] = mapped_column(
        ForeignKey("survey_defect.id"),
        comment="ID конкретного дефекта",
    )
    survey_defect_photo: Mapped["SurveyDefect"] = relationship(
        "SurveyDefect",
        back_populates="photos",
    )


# TODO: (Требует миграции) Сделать ограничение на обязательное существование связи:
# __table_args__ = (
#         CheckConstraint(
#             '(defect_type_id IS NOT NULL) OR (survey_id IS NOT NULL) OR (survey_defect_id IS NOT NULL)',
#             name='ck_photo_at_least_one_link'
#         ),
#     )
