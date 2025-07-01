from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_async_session
from app.models import DefectType
from app.repositories.base import BaseRepository
from app.schemas import DefectTypeCreate, DefectTypeUpdate


class DefectTypeRepository(
    BaseRepository[DefectType, DefectTypeCreate, DefectTypeUpdate]
):
    model = DefectType

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get(self, id: int) -> DefectType | None:
        statement = (
            select(self.model)
            .options(selectinload(self.model.images))
            .where(self.model.id == id)
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[DefectType]:
        statement = (
            select(self.model)
            .options(selectinload(self.model.images))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        result = await self.session.execute(statement=statement)
        return result.scalars().all()
