from typing import TYPE_CHECKING

from app.core.db import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Sector, Team, Ticket


class User(SQLAlchemyBaseUserTable[int], Base):
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True
    )
    name: Mapped[str | None] = mapped_column(String(255), unique=False)
    created_tickets: Mapped["Ticket"] = relationship(
        "Ticket", foreign_keys="Ticket.author_id", back_populates="author"
    )
    curated_tickets: Mapped["Ticket"] = relationship(
        "Ticket", foreign_keys="Ticket.curator_id", back_populates="curator"
    )
    lead_team: Mapped["Team"] = relationship(
        "Team", back_populates="leader", uselist=False
    )
    curated_sectors: Mapped["Sector"] = relationship(
        "Sector", back_populates="curator"
    )
