from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import DEFAULT_LIMIT
from app.core.db import get_async_session
from app.models import Survey, SurveyDefect, Tree
from app.repositories.base import BaseRepository
from app.schemas import SurveyDefectCreate, SurveyDefectUpdate


class SurveyDefectRepository(
    BaseRepository[SurveyDefect, SurveyDefectCreate, SurveyDefectUpdate]
):
    model = SurveyDefect

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get_all_by_survey_id(
        self, survey_id: int
    ) -> Sequence[SurveyDefect]:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.survey)
                .selectinload(Survey.tree)
                .selectinload(Tree.sector)
            )
            .where(self.model.survey_id == survey_id)
        )
        defects_db = await self.session.execute(statement=statement)
        return defects_db.scalars().all()

    async def get(self, id: int) -> SurveyDefect | None:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.survey)
                .selectinload(Survey.tree)
                .selectinload(Tree.sector)
            )
            .options(selectinload(self.model.photos))
            .where(self.model.id == id)
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[SurveyDefect]:
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.survey)
                .selectinload(Survey.tree)
                .selectinload(Tree.sector)
            )
            .options(selectinload(self.model.photos))
            .offset(offset=skip)
            .limit(limit=limit)
        )
        result = await self.session.execute(statement=statement)
        return result.scalars().all()
