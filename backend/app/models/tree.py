from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.schemas.enums import TreeConditionEnum

if TYPE_CHECKING:
    from app.models import Sector, User


class Tree(
    IntIdPkMixin,
    Base,
):
    """Модель описывающая растение (дерево)."""

    planting: Mapped[str] = mapped_column(
        String(length=50), comment="Вид насаждений"
    )
    species: Mapped[str] = mapped_column(
        String(length=50), comment="Порода растения"
    )
    description: Mapped[str] = mapped_column(Text, comment="Описание растения")
    location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
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
        default=TreeConditionEnum.HEALTHY,
        server_default=TreeConditionEnum.HEALTHY.name,
        comment="КСО",
    )
    is_emergency: Mapped[bool] = mapped_column(
        default=False,
        server_default="False",
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
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время создания записи",
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время изменения записи",
    )
