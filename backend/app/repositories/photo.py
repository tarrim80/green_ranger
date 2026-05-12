from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.validators import validate_photo_links
from app.core.db import get_async_session
from app.models import Photo
from app.models import Survey, Tree, SurveyDefect

from app.repositories.base import BaseRepository
from app.schemas import PhotoCreate, PhotoUpdate


class PhotoRepository(BaseRepository[Photo, PhotoCreate, PhotoUpdate]):
    """Репозиторий для работы с моделью фотографий."""

    model = Photo

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)

    async def get(self, id: int) -> Photo | None:
        """Получает фото по ID с загрузкой связанных сущностей."""
        statement = (
            select(self.model)
            .options(
                selectinload(self.model.tree_photo)
                .selectinload(Survey.tree)
                .selectinload(Tree.sector)
            )
            .options(
                selectinload(self.model.survey_defect_photo)
                .selectinload(SurveyDefect.survey)
                .selectinload(Survey.tree)
                .selectinload(Tree.sector)
            )
            .where(self.model.id == id)
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def update(self, db_obj: Photo, obj_in: PhotoUpdate) -> Photo:
        """Обновляет фотографию с валидацией наличия связей."""
        obj_data = {
            c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns
        }
        update_data = obj_in.model_dump(exclude_unset=True)
        obj_data.update(update_data)

        validate_photo_links(data=obj_data)

        return await super().update(db_obj=db_obj, obj_in=obj_in)
