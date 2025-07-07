from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEFAULT_LIMIT
from app.core.db import get_async_session
from app.models import Sector
from app.repositories.base import BaseRepository
from app.schemas import SectorCreate, SectorUpdate


class SectorRepository(BaseRepository[Sector, SectorCreate, SectorUpdate]):
    model = Sector

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get(self, id: int) -> Sector | None:
        result = await self.session.execute(
            statement=select(self.model)
            .options(selectinload(self.model.trees))
            .options(selectinload(self.model.curator))
            .options(selectinload(self.model.team))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[Sector]:
        result = await self.session.execute(
            statement=select(self.model)
            .options(selectinload(self.model.trees))
            .options(selectinload(self.model.curator))
            .options(selectinload(self.model.team))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        return result.scalars().all()
