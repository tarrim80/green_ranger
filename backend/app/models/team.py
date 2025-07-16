from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from app.models import Sector, User


class Team(
    IntIdPkMixin,
    Base,
):
    """Модель команды волонтеров."""

    __verbose_name__ = "Команда волонтеров"
    __verbose_name_plural__ = "Команды волонтеров"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, comment="Название команды"
    )
    leader_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID лидера команды",
    )
    leader: Mapped["User"] = relationship(
        "User", foreign_keys=[leader_id], back_populates="lead_team"
    )
    members: Mapped[list["User"]] = relationship(
        "User", back_populates="team", primaryjoin="Team.id==User.team_id"
    )
    sectors: Mapped[list["Sector"]] = relationship(
        "Sector", back_populates="team"
    )
