"""Импорты класса Base и всех моделей для Alembic."""

from app.core.db import Base
from app.models import (
    Damage,
    Photo,
    Sector,
    Team,
    Ticket,
    TicketDamage,
    TicketDamagePhoto,
    TicketPhoto,
    User,
)
