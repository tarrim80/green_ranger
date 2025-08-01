from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEFAULT_LIMIT
from app.core.db import get_async_session
from app.models import DefectType
from app.repositories.base import BaseRepository
from app.schemas import DefectTypeCreate, DefectTypeUpdate


class DefectTypeRepository(
    BaseRepository[DefectType, DefectTypeCreate, DefectTypeUpdate]
):
    """Репозиторий для работы с моделью вида дефектов."""

    model = DefectType

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get(self, id: int) -> DefectType | None:
        """Получает вид дефекта по ID с загрузкой связанных изображений."""
        statement = (
            select(self.model)
            .options(selectinload(self.model.images))
            .where(self.model.id == id)
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[DefectType]:
        """Получает список видов дефектов с загрузкой изображений."""
        statement = (
            select(self.model)
            .options(selectinload(self.model.images))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        result = await self.session.execute(statement=statement)
        return result.scalars().all()
