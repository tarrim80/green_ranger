from typing import TYPE_CHECKING

from app.core.db import Base
from app.models.enums import DamageStatusEnum
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Photo, Ticket


class Damage(Base):
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        comment="Наименование типа повреждения",
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Общее описание типа повреждения"
    )
    ticket_damages: Mapped[list["TicketDamage"]] = relationship(
        "TicketDamage", back_populates="damage_type"
    )


class TicketDamage(Base):

    __tablename__ = "ticket_damage"

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("ticket.id"), nullable=False, comment="ID заявки"
    )
    damage_id: Mapped[int] = mapped_column(
        ForeignKey("damage.id"),
        nullable=False,
        comment="ID типа повреждения из справочника",
    )
    damage_status: Mapped[DamageStatusEnum] = mapped_column(
        ENUM(
            DamageStatusEnum,
            name="damage_status_enum",
        ),
        nullable=False,
        comment="Код статуса обработки этого повреждения",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Описание повреждения",
    )

    ticket: Mapped["Ticket"] = relationship(
        "Ticket",
        back_populates="damages",
    )
    damage_type: Mapped[Damage] = relationship(
        "Damage",
        back_populates="ticket_damages",
    )
    photos: Mapped[list["Photo"]] = relationship(
        "Photo",
        secondary="ticket_damage_photo",
        back_populates="damages_photo",
    )
