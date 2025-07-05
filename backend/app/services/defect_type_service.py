import os
from pathlib import Path

from fastapi import Depends, UploadFile
from sqlalchemy.exc import IntegrityError

from app.core.constants import ExceptionDetails
from app.core.exceptions import (
    DefectTypeCreationError,
    DefectTypeRemovingError,
    NotFoundError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import DefectType, Photo
from app.repositories.defect_type import DefectTypeRepository
from app.schemas import DefectTypeCreate
from app.services.photo_service import PhotoService
from app.utils.photo_uploader import save_uploaded_images


class DefectTypeService:
    def __init__(
        self,
        repo: DefectTypeRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def create_with_photos(
        self, defect_type_in: DefectTypeCreate, files: list[UploadFile]
    ) -> DefectType:
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = defect_type_in.model_dump()
            new_defect_type = DefectType(**new_data)
            self.repo.session.add(instance=new_defect_type)
            await self.repo.session.flush()
            for photo_data in photos_data:
                new_data = {
                    "file_path": photo_data["file_path"],
                    "defect_type_id": new_defect_type.id,
                }
                new_photo = Photo(**new_data)
                self.repo.session.add(instance=new_photo)
            await self.repo.session.commit()
            await self.repo.session.refresh(
                instance=new_defect_type, attribute_names=["images"]
            )
            return new_defect_type
        except Exception as e:
            await self.repo.session.rollback()
            for filename in saved_file_paths:
                os.remove(filename)

            if isinstance(e, IntegrityError):
                raise DefectTypeCreationError(
                    ExceptionDetails.ALREADY_EXIST_DEFECT_TYPE_NAME
                )
            raise DefectTypeCreationError(
                f"{ExceptionDetails.FAILED_CREATE_DEFECT_TYPE}: {e}"
            )

    async def _stage_deletion(self, defect_type_id: int) -> list[Path]:
        defect_type_db = await self.repo.get(id=defect_type_id)
        if not defect_type_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name="Вид дефекта", id=defect_type_id
                )
            )
        images_to_delete: list[Path] = []
        for image in defect_type_db.images:
            image_path = await self.photo_service._stage_deletion(
                photo_id=image.id
            )
            images_to_delete.append(image_path)
        await self.repo.remove(id=defect_type_id)
        return images_to_delete

    async def delete_with_images(self, defect_type_id: int) -> None:
        try:
            async with atomic_transaction(session=self.repo.session):
                images_to_delete = await self._stage_deletion(
                    defect_type_id=defect_type_id
                )
            if images_to_delete:
                for path in images_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except NotFoundError:
            raise
        except Exception as e:
            raise DefectTypeRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_DEFECT_TYPE}: {e}"
            ) from e
