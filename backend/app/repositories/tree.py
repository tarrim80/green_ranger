from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEFAULT_LIMIT
from app.core.db import get_async_session
from app.models import Tree
from app.repositories.base import BaseRepository
from app.schemas import TreeCreate, TreeUpdate


class TreeRepository(BaseRepository[Tree, TreeCreate, TreeUpdate]):
    """Репозиторий для работы с моделью растений (деревьев)."""

    model = Tree

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get_all_by_sector_id(self, sector_id: int) -> Sequence[Tree]:
        """Получает все растения для конкретного учетного участка."""

        result = await self.session.execute(
            statement=select(self.model)
            .options(selectinload(self.model.sector))
            .options(selectinload(self.model.author))
            .options(selectinload(self.model.surveys))
            .where(self.model.sector_id == sector_id)
        )
        return result.scalars().all()

    async def get(self, id: int) -> Tree | None:
        """Получает команду по ID с загрузкой участников."""
        result = await self.session.execute(
            statement=select(self.model)
            .options(selectinload(self.model.sector))
            .options(selectinload(self.model.author))
            .options(selectinload(self.model.surveys))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[Tree]:
        """Получает список команд с загрузкой участников."""
        result = await self.session.execute(
            statement=select(self.model)
            .options(selectinload(self.model.sector))
            .options(selectinload(self.model.author))
            .options(selectinload(self.model.surveys))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        return result.scalars().all()
