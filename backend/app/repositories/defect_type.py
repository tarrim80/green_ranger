from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import DefectType
from app.repositories.base import BaseRepository
from app.repositories.photo import PhotoRepository
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
        photo_repo: Annotated[PhotoRepository, Depends()],
    ) -> None:
        super().__init__(session=session)
        self.photo_repo = photo_repo

    async def create(self, obj_in: DefectTypeCreate) -> DefectType:
        obj_data = obj_in.model_dump()
        image_ids = obj_data.pop("image_ids", [])
        new_defect_type = self.model(**obj_data)
        if image_ids:
            images = await self.photo_repo.get_by_ids(ids=image_ids)
            if len(images) != len(image_ids):
                # TODO: Бросить ошибку, если не все фото найдены
                pass
            new_defect_type.images = images

        self.session.add(instance=new_defect_type)
        await self.session.commit()
        await self.session.refresh(instance=new_defect_type)
        return new_defect_type
