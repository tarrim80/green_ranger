from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from app.models.user import User


class Role(
    IntIdPkMixin,
    Base,
):
    """Роли пользователей."""

    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    users: Mapped[list["User"]] = relationship(
        secondary="user_roles", back_populates="roles"
    )
