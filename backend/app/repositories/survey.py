from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import Survey
from app.repositories.base import BaseRepository
from app.schemas import SurveyCreate, SurveyUpdate


class SurveyRepository(BaseRepository[Survey, SurveyCreate, SurveyUpdate]):
    model = Survey

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)
