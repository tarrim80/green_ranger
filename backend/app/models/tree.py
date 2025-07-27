from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import SRID_MERCATOR_WGS84
from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.schemas.defaults import TreeDefaults
from app.schemas.enums import TreeConditionEnum

if TYPE_CHECKING:
    from app.models import Sector, User


class Tree(
    IntIdPkMixin,
    Base,
):
    """Модель описывающая растение (дерево)."""

    __verbose_name__ = "Растение"
    __verbose_name_plural__ = "Растения"

    planting: Mapped[str] = mapped_column(
        String(length=50), comment="Вид насаждений"
    )
    species: Mapped[str] = mapped_column(
        String(length=50), comment="Порода растения"
    )
    description: Mapped[str] = mapped_column(Text, comment="Описание растения")
    location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=SRID_MERCATOR_WGS84),
        comment="Местоположение растения",
    )
    azimuth: Mapped[float | None] = mapped_column(
        comment="Азимут от точки привязки до растения"
    )
    distance: Mapped[float | None] = mapped_column(
        comment="Расстояние от точки привязки до растения в метрах"
    )
    sector_id: Mapped[int] = mapped_column(
        ForeignKey("sector.id"),
        comment="Учетный участок",
    )
    sector: Mapped["Sector"] = relationship("Sector", back_populates="trees")
    condition: Mapped[TreeConditionEnum] = mapped_column(
        ENUM(TreeConditionEnum, name="tree_condition_enum"),
        default=TreeDefaults.CONDITION,
        server_default=TreeDefaults.CONDITION.name,
        comment="КСО",
    )
    is_emergency: Mapped[bool] = mapped_column(
        default=TreeDefaults.IS_EMERGENCY,
        server_default=str(TreeDefaults.IS_EMERGENCY),
        comment="Признак аварийности/срочности",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID автора регистрации растения",
    )
    author: Mapped["User"] = relationship(
        "User",
        back_populates="registered_trees",
    )
    # TODO: Изменить на DateTime(timezone=True) и создать миграцию
    # для корректной работы с часовыми поясами.
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время создания записи",
    )
    # TODO: Изменить на DateTime(timezone=True) и создать миграцию
    # для корректной работы с часовыми поясами.
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время изменения записи",
    )
