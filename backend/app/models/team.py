from typing import TYPE_CHECKING

from app.core.db import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Sector, User


class Team(Base):
    name: Mapped[str] = mapped_column(
        String(50), unique=True, comment="Название команды"
    )
    leader_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        unique=True,
        comment="ID пользователя-лидера команды",
    )
    leader: Mapped["User"] = relationship("User", back_populates="lead_team")
    sectors: Mapped[list["Sector"]] = relationship(
        "Sector", back_populates="team"
    )
