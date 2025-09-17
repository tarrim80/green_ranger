from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEFAULT_LIMIT
from app.core.db import get_async_session
from app.models import Survey, Tree
from app.repositories.base import BaseRepository
from app.schemas import SurveyCreate, SurveyUpdate


class SurveyRepository(BaseRepository[Survey, SurveyCreate, SurveyUpdate]):
    """Репозиторий для работы с моделью обследований."""

    model = Survey

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get(self, id: int) -> Survey | None:
        """Получает обследование по ID с загрузкой связанных сущностей."""
        statement = (
            select(self.model)
            .options(selectinload(self.model.tree).selectinload(Tree.sector))
            .options(selectinload(self.model.tree_photos))
            .options(selectinload(self.model.survey_defects))
            .options(selectinload(self.model.author))
            .where(self.model.id == id)
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[Survey]:
        """Получает список обследований с загрузкой связанных сущностей."""
        statement = (
            select(self.model)
            .options(selectinload(self.model.tree).selectinload(Tree.sector))
            .options(selectinload(self.model.tree_photos))
            .options(selectinload(self.model.survey_defects))
            .options(selectinload(self.model.author))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        result = await self.session.execute(statement=statement)
        return result.scalars().all()

    async def get_all_by_tree_id(self, tree_id: int) -> Sequence[Survey]:
        """Получает все обследования для конкретного растения."""
        statement = (
            select(self.model)
            .options(selectinload(self.model.tree).selectinload(Tree.sector))
            .options(selectinload(self.model.tree_photos))
            .options(selectinload(self.model.survey_defects))
            .options(selectinload(self.model.author))
            .where(self.model.tree_id == tree_id)
        )
        surveys_db = await self.session.execute(statement=statement)
        return surveys_db.scalars().all()
