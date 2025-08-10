import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
    SurveyDefectCreationError,
    SurveyDefectRemovingError,
    SurveyDefectUpdatingError,
)
from app.core.permissions import (
    IsSurveyDefectOwnerOrCurator,
    IsTreeCuratorOrCorrectTeam,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Photo, Survey, SurveyDefect, Tree, User
from app.repositories.survey import SurveyRepository
from app.repositories.survey_defect import SurveyDefectRepository
from app.repositories.tree import TreeRepository
from app.schemas import SurveyDefectCreate, SurveyDefectUpdate
from app.services.mixins.base_update import UpdateObjMixin
from app.services.photo_service import PhotoService
from app.utils.photo_uploader import save_uploaded_images


class SurveyDefectService(UpdateObjMixin):
    """Сервисный слой для управления обнаруженными дефектами."""

    def __init__(
        self,
        repo: SurveyDefectRepository = Depends(),
        survey_repo: SurveyRepository = Depends(),
        tree_repo: TreeRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.survey_repo = survey_repo
        self.tree_repo = tree_repo
        self.photo_service = photo_service

    async def get_all_defects(self) -> list[SurveyDefect]:
        """Получает список всех дефектов."""
        defects_db = await self.repo.get_multi()
        return list(defects_db)

    async def get_defect(self, obj_id: int) -> SurveyDefect:
        """Получает дефект по его идентификатору."""
        defect_db = await self.repo.get(id=obj_id)
        if not defect_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return defect_db

    async def get_defects_by_survey_id(
        self, survey_id: int
    ) -> list[SurveyDefect]:
        """Получает список всех дефектов для конкретного обследования."""
        defects_db = await self.repo.get_all_by_survey_id(survey_id=survey_id)
        return list(defects_db)

    async def create_with_photos(
        self,
        survey_defect_in: SurveyDefectCreate,
        files: list[UploadFile],
        user: User,
    ) -> SurveyDefect:
        """Создает новый дефект с привязкой фотографий."""
        saved_file_paths = []
        try:
            survey_db = await self.survey_repo.get(
                id=survey_defect_in.survey_id
            )
            if not survey_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.survey_repo.model.verbose_name(),
                        id=survey_defect_in.survey_id,
                    )
                )
            permission = await IsTreeCuratorOrCorrectTeam().has_obj_permission(
                user=user, obj=survey_db.tree
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = survey_defect_in.model_dump()
            new_survey_defect = SurveyDefect(**new_data)
            async with atomic_transaction(session=self.repo.session):
                self.repo.session.add(instance=new_survey_defect)
                await self.repo.session.flush()
                for photo_data in photos_data:
                    new_data = {
                        "file_path": photo_data["file_path"],
                        "thumbnail_path": photo_data["thumbnail_path"],
                        "survey_defect_id": new_survey_defect.id,
                    }
                    new_photo = Photo(**new_data)
                    self.repo.session.add(instance=new_photo)
                await self.repo.session.refresh(
                    instance=new_survey_defect, attribute_names=["photos"]
                )
            return new_survey_defect
        except (NotFoundError, PermissionDenniedError):
            raise
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyDefectCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY_DEFECT}: {e}"
            )

    async def update_defect(
        self, obj_id: int, obj_in: SurveyDefectUpdate, user: User
    ) -> SurveyDefect:
        """Обновляет данные существующего дефекта с проверкой прав доступа."""
        try:
            defect_db = await self.repo.get(id=obj_id)
            if not defect_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=user, obj=defect_db
                )
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            defect = await self.update_obj(db_obj=defect_db, obj_in=obj_in)
            return defect
        except (NotFoundError, PermissionDenniedError):
            raise
        except Exception as e:
            raise SurveyDefectUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(
        self, defect_db: SurveyDefect, user: User
    ) -> list[Path]:
        """Подготавливает дефект и связанные фотографии к удалению."""
        paths_photo_to_delete = []
        for photo in defect_db.photos:
            paths_defect_photo = await self.photo_service._stage_deletion(
                photo_id=photo.id, user=user
            )
            paths_photo_to_delete.extend(paths_defect_photo)
        await self.repo.remove(id=defect_db.id)
        return paths_photo_to_delete

    async def delete_with_photos(self, defect_id: int, user: User) -> None:
        """
        Удаляет дефект, связанные фотографии и записи в БД с проверкой прав.
        """
        try:
            defect_db = await self.repo.get(id=defect_id)
            if not defect_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(), id=defect_id
                    )
                )
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=user, obj=defect_db
                )
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            async with atomic_transaction(session=self.repo.session):
                paths_photo_to_delete = await self._stage_deletion(
                    defect_db=defect_db, user=user
                )
            if paths_photo_to_delete:
                for path in paths_photo_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except (NotFoundError, PermissionDenniedError):
            raise
        except Exception as e:
            raise SurveyDefectRemovingError(
                f"{ExceptionDetails.FAILED_ROMOVE_SURVEY_DEFECT}: {e}"
            ) from e
