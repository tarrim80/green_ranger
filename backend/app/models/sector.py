from typing import TYPE_CHECKING

from app.core.db import Base
from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Team, Ticket, User


class Sector(Base):
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        comment="Название или номер сектора",
    )
    curator_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID куратора сектора",
    )
    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("team.id"),
        comment="ID команды, назначенной на участок",
    )
    color: Mapped[str] = mapped_column(
        String(7),
        default="#000000",
        comment="Цвет для отображения сектора на карте (HEX)",
    )
    geometry: Mapped[Geometry] = mapped_column(
        Geometry("POLYGON", srid=4326),
        comment="Геометрия (полигон) сектора",
    )

    curator: Mapped["User"] = relationship(
        "User", back_populates="curated_sectors"
    )
    team: Mapped["Team"] = relationship("Team", back_populates="sectors")
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket", back_populates="sector"
    )
