import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.config import settings
from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PhotoCreationError,
    PhotoRemovingError,
    PhotoUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Photo
from app.repositories.photo import PhotoRepository
from app.schemas import PhotoCreate, PhotoUpdate
from app.services.mixins import UpdateObjMixin
from app.utils.photo_uploader import save_uploaded_images


class PhotoService(UpdateObjMixin):
    """Сервисный слой для управления фотографиями."""

    def __init__(self, repo: PhotoRepository = Depends()) -> None:
        self.repo = repo

    async def upload_and_link_photos(
        self,
        files: list[UploadFile],
        defect_type_id: int | None = None,
        survey_id: int | None = None,
        survey_defect_id: int | None = None,
    ) -> list[Photo]:
        """Загружает, обрабатывает и привязывает фотографии к сущностям."""
        saved_file_paths = []
        photos_to_create = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            for photo_data in photos_data:
                relative_path = photo_data["file_path"]
                photo_in = PhotoCreate(
                    file_path=relative_path,
                    defect_type_id=defect_type_id,
                    survey_id=survey_id,
                    survey_defect_id=survey_defect_id,
                )
                photos_to_create.append(photo_in)
            async with atomic_transaction(session=self.repo.session):
                photos_db = await self.repo.create_many(
                    objs_in=photos_to_create
                )
            return photos_db
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(path=filename)
            raise PhotoCreationError(
                f"{ExceptionDetails.FAILED_CREATE_PHOTO}: {e}"
            )

    async def update_photo(self, obj_id: int, obj_in: PhotoUpdate) -> Photo:
        """Обновляет связи существующей фотографии."""
        try:
            photo_db = await self.repo.get(id=obj_id)
            if not photo_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            photo = await self.update_obj(db_obj=photo_db, obj_in=obj_in)
            return photo
        except (ValueError, NotFoundError):
            raise
        except Exception as e:
            raise PhotoUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(self, photo_id: int) -> Path:
        """Подготавливает файл фотографии к физическому удалению с диска."""
        photo_db = await self.repo.get(id=photo_id)
        if not photo_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(), id=photo_id
                )
            )
        await self.repo.remove(id=photo_id)
        file_to_delete = settings.media_root / photo_db.file_path
        return file_to_delete

    async def delete_photo(self, photo_id: int) -> None:
        """Удаляет фотографию из базы данных и с диска."""
        try:
            async with atomic_transaction(session=self.repo.session):
                path_to_delete = await self._stage_deletion(photo_id=photo_id)
            if os.path.exists(path=path_to_delete):
                os.remove(path=path_to_delete)
        except NotFoundError:
            raise
        except Exception as e:
            raise PhotoRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_PHOTO}: {e}"
            ) from e
