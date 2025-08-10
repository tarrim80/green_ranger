import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.config import settings
from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
    PhotoCreationError,
    PhotoRemovingError,
)
from app.core.permissions import (
    IsAdmin,
    IsSurveyDefectOwnerOrCurator,
    IsSurveyOwnerOrCurator,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Photo, User
from app.repositories.photo import PhotoRepository
from app.repositories.survey import SurveyRepository
from app.repositories.survey_defect import SurveyDefectRepository
from app.schemas import PhotoCreate
from app.services.mixins import UpdateObjMixin
from app.utils.photo_uploader import save_uploaded_images


class PhotoService(UpdateObjMixin):
    """Сервисный слой для управления фотографиями."""

    def __init__(
        self,
        repo: PhotoRepository = Depends(),
        survey_repo: SurveyRepository = Depends(),
        defect_repo: SurveyDefectRepository = Depends(),
    ) -> None:
        self.repo = repo
        self.survey_repo = survey_repo
        self.defect_repo = defect_repo

    async def upload_and_link_photos(
        self,
        files: list[UploadFile],
        user: User,
        defect_type_id: int | None = None,
        survey_id: int | None = None,
        survey_defect_id: int | None = None,
    ) -> list[Photo]:
        if defect_type_id:
            permission = await IsAdmin().has_permission(user=user)
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
        if survey_id:
            survey = await self.survey_repo.get(id=survey_id)
            if not survey:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.survey_repo.model.verbose_name(),
                        id=survey_id,
                    )
                )
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=user, obj=survey
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
        if survey_defect_id:
            survey_defect = await self.defect_repo.get(id=survey_defect_id)
            if not survey_defect:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.defect_repo.model.verbose_name(),
                        id=survey_defect_id,
                    )
                )
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=user, obj=survey_defect
                )
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )

        saved_images_data, saved_file_paths = await save_uploaded_images(
            files=files
        )

        try:
            photos_to_create = []
            for image_data in saved_images_data:
                photo_in = PhotoCreate(
                    **image_data,
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
            for path in saved_file_paths:
                if os.path.exists(path):
                    os.remove(path)
            raise PhotoCreationError(
                f"{ExceptionDetails.FAILED_CREATE_PHOTO}: {e}"
            )

    async def _stage_deletion(self, photo_id: int, user: User) -> list[Path]:
        """Подготавливает файл фотографии к физическому удалению с диска."""
        photo_db: Photo = await self.repo.get(id=photo_id)
        if not photo_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(), id=photo_id
                )
            )
        if photo_db.defect_type_id:
            permission = await IsAdmin().has_permission(user=user)
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
        if photo_db.survey_id:
            survey = await self.survey_repo.get(id=photo_db.survey_id)
            if not survey:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.survey_repo.model.verbose_name(),
                        id=photo_db.survey_id,
                    )
                )
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=user, obj=survey
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
        if photo_db.survey_defect_id:
            survey_defect = await self.defect_repo.get(
                id=photo_db.survey_defect_id
            )
            if not survey_defect:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.defect_repo.model.verbose_name(),
                        id=photo_db.survey_defect_id,
                    )
                )
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=user, obj=survey_defect
                )
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
        paths_photo_to_delete = [
            settings.media_root / photo_db.file_path,
            settings.media_root / photo_db.thumbnail_path,
        ]

        await self.repo.remove(id=photo_id)
        return paths_photo_to_delete

    async def delete_photo(self, photo_id: int, user: User) -> None:
        """Удаляет фотографию из базы данных и с диска."""
        try:
            async with atomic_transaction(session=self.repo.session):
                paths_photo_to_delete = await self._stage_deletion(
                    photo_id=photo_id, user=user
                )
            for path in paths_photo_to_delete:
                if os.path.exists(path=path):
                    os.remove(path=path)
        except (NotFoundError, PermissionDenniedError):
            raise
        except Exception as e:
            raise PhotoRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_PHOTO}: {e}"
            ) from e
