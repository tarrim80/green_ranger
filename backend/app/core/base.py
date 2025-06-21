"""Импорты класса Base и всех моделей для Alembic."""

from app.core.db import Base
from app.models import (
    Defect,
    Photo,
    Sector,
    Team,
    Ticket,
    TicketDefect,
    TicketDefectPhoto,
    TicketPhoto,
    User,
)
