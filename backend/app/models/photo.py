from typing import TYPE_CHECKING

from app.core.db import Base
from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Ticket, TicketDamage


class Photo(Base):
    file_path: Mapped[str] = mapped_column(
        String(255),
        comment="Путь к файлу изображения на сервере",
    )
    uploaded_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время загрузки фото",
    )

    tickets_photo: Mapped[list["Ticket"]] = relationship(
        "Ticket", secondary="ticket_photo", back_populates="photos"
    )
    damages_photo: Mapped["TicketDamage"] = relationship(
        "TicketDamage",
        secondary="ticket_damage_photo",
        back_populates="photos",
    )


class TicketDamagePhoto(Base):

    __tablename__ = "ticket_damage_photo"

    ticket_damage_id: Mapped[int] = mapped_column(
        ForeignKey("ticket_damage.id"),
        comment="ID зафиксированного повреждения",
    )
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photo.id"),
        comment="ID фотографии",
    )


class TicketPhoto(Base):

    __tablename__ = "ticket_photo"

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("ticket.id"),
        comment="ID заявки",
    )
    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photo.id"),
        comment="ID фотографии",
    )
