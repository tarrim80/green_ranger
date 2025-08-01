from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import validate_photo_links
from app.core.db import get_async_session
from app.models import Photo
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

    async def update(self, db_obj: Photo, obj_in: PhotoUpdate) -> Photo:
        """Обновляет фотографию с валидацией наличия связей."""
        obj_data = {
            c.name: getattr(db_obj, c.name) for c in db_obj.__table__.columns
        }
        update_data = obj_in.model_dump(exclude_unset=True)
        obj_data.update(update_data)

        validate_photo_links(data=obj_data)

        return await super().update(db_obj=db_obj, obj_in=obj_in)
