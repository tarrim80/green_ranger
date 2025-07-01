import os

from fastapi import Depends, UploadFile
from sqlalchemy.exc import IntegrityError

from app.core.constants import ExceptionDetails
from app.core.exceptions import DefectTypeCreationError, NotFoundError
from app.models import DefectType, Photo
from app.repositories.defect_type import DefectTypeRepository
from app.services.photo_uploader import save_uploaded_images

from .photo_service import PhotoService


class DefectTypeService:
    def __init__(
        self,
        repo: DefectTypeRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def create_with_photos(
        self, name: str, description: str | None, files: list[UploadFile]
    ) -> DefectType:
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = {"name": name, "description": description}
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

    async def delete_with_photos(
        self, defect_type_id: int
    ) -> None | DefectType:
        defect_type_db = await self.repo.get(id=defect_type_id)
        if not defect_type_db:
            return None
        for image in defect_type_db.images:
            await self.photo_service.delete_photo_file(photo_id=image.id)
        return await self.repo.remove(id=defect_type_id)
