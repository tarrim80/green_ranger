from typing import TYPE_CHECKING

from app.core.db import Base
from app.models.enums import TicketStatusEnum, TreeConditionEnum
from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models import Photo, Sector, TicketDamage, User


class Ticket(Base):
    planting: Mapped[str] = mapped_column(
        String(length=50), comment="Вид насаждений"
    )
    species: Mapped[str] = mapped_column(
        String(length=50), comment="Порода растения"
    )
    description: Mapped[str] = mapped_column(Text, comment="Описание растения")
    age: Mapped[int | None] = mapped_column(comment="Возраст растения")
    height: Mapped[float | None] = mapped_column(
        comment="Высота растения в метрах"
    )
    diameter: Mapped[float | None] = mapped_column(
        comment="Диаметр ствола на высоте груди в см"
    )
    trunk_count: Mapped[int] = mapped_column(
        default=1, comment="Количество стволов"
    )
    condition: Mapped[TreeConditionEnum] = mapped_column(
        ENUM(TreeConditionEnum, name="tree_condition_enum"),
        default=TreeConditionEnum.HEALTHY,
        comment="КСО",
    )
    location: Mapped[Geometry] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326),
        comment="Местоположение растения",
    )
    azimuth: Mapped[float | None] = mapped_column(
        comment="Азимут от точки привязки"
    )
    distance: Mapped[float | None] = mapped_column(
        comment="Расстояние от точки привязки в метрах"
    )
    sector_id: Mapped[int] = mapped_column(
        ForeignKey("sector.id"),
        comment="Учетный участок",
    )
    curator_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID куратора участка",
    )
    is_emergency: Mapped[bool] = mapped_column(
        default=False,
        comment="Признак аварийности/срочности",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        comment="ID автора заявки",
    )
    ticket_status: Mapped[TicketStatusEnum] = mapped_column(
        ENUM(TicketStatusEnum, name="ticket_status_enum"),
        default=TicketStatusEnum.NEW,
        comment="Код статуса заявки",
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="Дата и время создания заявки",
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Дата и время изменения заявки",
    )

    sector: Mapped["Sector"] = relationship("Sector", back_populates="tickets")
    curator: Mapped["User"] = relationship(
        "User",
        foreign_keys="Ticket.curator_id",
        back_populates="curated_tickets",
    )
    author: Mapped["User"] = relationship(
        "User",
        foreign_keys="Ticket.author_id",
        back_populates="created_tickets",
    )
    damages: Mapped["TicketDamage"] = relationship(
        "TicketDamage", back_populates="ticket", cascade="all, delete-orphan"
    )
    photos: Mapped["Photo"] = relationship(
        "Photo", secondary="ticket_photo", back_populates="tickets_photo"
    )
