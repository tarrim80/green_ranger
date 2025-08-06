import os
from pathlib import Path

from fastapi import Depends, UploadFile
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    DefectTypeCreationError,
    DefectTypeRemovingError,
    DefectTypeUpdatingError,
    ExceptionDetails,
    NotFoundError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import DefectType, Photo
from app.repositories.defect_type import DefectTypeRepository
from app.schemas import DefectTypeCreate, DefectTypeUpdate
from app.services.mixins import UpdateObjMixin
from app.services.photo_service import PhotoService
from app.utils.photo_uploader import save_uploaded_images


class DefectTypeService(UpdateObjMixin):
    """Сервисный слой для управления видами дефектов."""

    def __init__(
        self,
        repo: DefectTypeRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def get_all_defect_types(self) -> list[DefectType]:
        """Получает список всех видов дефектов."""
        defect_types_db = await self.repo.get_multi()
        return defect_types_db

    async def get_defect_type(self, obj_id: int) -> DefectType:
        """Получает вид дефекта по его идентификатору."""
        defect_type_db = await self.repo.get(id=obj_id)
        if not defect_type_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return defect_type_db

    async def create_with_photos(
        self, defect_type_in: DefectTypeCreate, files: list[UploadFile]
    ) -> DefectType:
        """Создает новый вид дефекта с привязкой фотографий."""
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = defect_type_in.model_dump()
            new_defect_type = DefectType(**new_data)
            async with atomic_transaction(session=self.repo.session):
                self.repo.session.add(instance=new_defect_type)
                await self.repo.session.flush()
                for photo_data in photos_data:
                    new_data = {
                        "file_path": photo_data["file_path"],
                        "thumbnail_path": photo_data["thumbnail_path"],
                        "defect_type_id": new_defect_type.id,
                    }
                    new_photo = Photo(**new_data)
                    self.repo.session.add(instance=new_photo)
                await self.repo.session.refresh(
                    instance=new_defect_type, attribute_names=["images"]
                )
            return new_defect_type
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            if isinstance(e, IntegrityError):
                raise DefectTypeCreationError(
                    ExceptionDetails.ALREADY_EXIST_DEFECT_TYPE_NAME
                )
            raise DefectTypeCreationError(
                f"{ExceptionDetails.FAILED_CREATE_DEFECT_TYPE}: {e}"
            )

    async def update_defect_type(
        self, obj_id: int, obj_in: DefectTypeUpdate
    ) -> DefectType:
        """Обновляет данные существующего вида дефекта."""
        try:
            defect_type_db = await self.repo.get(id=obj_id)
            if not defect_type_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            defect_type = await self.update_obj(
                db_obj=defect_type_db, obj_in=obj_in
            )
            return defect_type
        except NotFoundError:
            raise
        except Exception as e:
            raise DefectTypeUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(self, defect_type_id: int) -> list[Path]:
        """Подготавливает вид дефекта и связанные изображения к удалению."""
        defect_type_db = await self.repo.get(id=defect_type_id)
        if not defect_type_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=defect_type_id,
                )
            )
        paths_image_to_delete = []
        for image in defect_type_db.images:
            paths_defect_type_image = await self.photo_service._stage_deletion(
                photo_id=image.id
            )
            paths_image_to_delete.extend(paths_defect_type_image)
        await self.repo.remove(id=defect_type_id)
        return paths_image_to_delete

    async def delete_with_images(self, defect_type_id: int) -> None:
        """Удаляет вид дефекта и все связанные с ним изображения."""
        try:
            async with atomic_transaction(session=self.repo.session):
                paths_image_to_delete = await self._stage_deletion(
                    defect_type_id=defect_type_id
                )
            if paths_image_to_delete:
                for path in paths_image_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except NotFoundError:
            raise
        except Exception as e:
            raise DefectTypeRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_DEFECT_TYPE}: {e}"
            ) from e
