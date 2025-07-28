from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import BigInteger, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.models.team import Team
from app.schemas import RoleEnum
from app.schemas.defaults import UserDefaults

if TYPE_CHECKING:
    from app.models import Sector, Survey, Tree


class User(SQLAlchemyBaseUserTable[int], IntIdPkMixin, Base):  # type: ignore
    """Модель пользователя. Расширение FastAPI User."""

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, comment="ID Telegram"
    )
    firstname: Mapped[str] = mapped_column(
        String(100), unique=False, comment="Имя"
    )
    lastname: Mapped[str] = mapped_column(
        String(100), unique=False, comment="Фамилия"
    )
    team_id: Mapped[int | None] = mapped_column(ForeignKey("team.id"))
    team: Mapped[Team] = relationship(
        "Team",
        foreign_keys=[team_id],
        back_populates="members",
    )
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"),
        default=UserDefaults.ROLE,
        server_default=UserDefaults.ROLE.name,
    )
    lead_team: Mapped[Team] = relationship(
        "Team",
        foreign_keys=[Team.leader_id],
        back_populates="leader",
    )
    created_surveys: Mapped[list["Survey"]] = relationship(
        "Survey", back_populates="author"
    )
    registered_trees: Mapped[list["Tree"]] = relationship(
        "Tree", back_populates="author"
    )
    curated_sectors: Mapped[list["Sector"]] = relationship(
        "Sector", back_populates="curator"
    )

    @property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __str__(self) -> str:
        return self.fullname
