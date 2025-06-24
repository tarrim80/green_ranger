from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import Base
from app.models.mixins.int_id_pk import IntIdPkMixin
from app.models.team import Team

if TYPE_CHECKING:
    from app.models import Role, Sector, Survey, Tree

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
)


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
        back_populates="members",
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
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles, back_populates="users", lazy="selectin"
    )

    @property
    def fullname(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def __str__(self) -> str:
        return self.fullname
