from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        statement = select(self.model).where(self.model.sector_id == sector_id)
        surveys_db = await self.session.execute(statement=statement)
        return surveys_db.scalars().all()
