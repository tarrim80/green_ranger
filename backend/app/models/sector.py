from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import SRID_MERCATOR_WGS84
from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.schemas.defaults import SectorDefaults

if TYPE_CHECKING:
    from app.models import Team, Tree, User


class Sector(
    IntIdPkMixin,
    Base,
):
    """Модель учетного участка."""

    __verbose_name__ = "Учетный участок"
    __verbose_name_plural__ = "Учетные участки"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        comment="Название или номер участка",
    )
    curator_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID куратора участка",
    )
    curator: Mapped["User"] = relationship(
        "User", back_populates="curated_sectors"
    )
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("team.id"),
        comment="ID команды, назначенной на участок",
    )
    team: Mapped["Team"] = relationship("Team", back_populates="sectors")
    color: Mapped[str] = mapped_column(
        String(7),
        default=SectorDefaults.COLOR,
        server_default=str(SectorDefaults.COLOR),
        comment="Цвет для отображения участка на карте (HEX)",
    )
    geometry: Mapped[Geometry] = mapped_column(
        Geometry("POLYGON", srid=SRID_MERCATOR_WGS84),
        comment="Геометрия (полигон) участка",
    )

    trees: Mapped[list["Tree"]] = relationship("Tree", back_populates="sector")
