import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.exceptions import (
    ExceptionDetails,
    SurveyDefectCreationError,
    SurveyDefectRemovingError,
    SurveyDefectUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import SurveyDefect
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
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def get_all_defects(self) -> list[SurveyDefect]:
        """Получает список всех дефектов."""
        defects_db = await self.repo.get_multi()
        return list(defects_db)

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
    ) -> SurveyDefect:
        """Создает новый дефект с привязкой фотографий."""
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = survey_defect_in.model_dump()
            new_survey_defect = SurveyDefect(**new_data)
            async with atomic_transaction(session=self.repo.session):
                self.repo.session.add(instance=new_survey_defect)
                await self.repo.session.flush()
                await self.photo_service.create_photo_batch(
                    photos_data=photos_data,
                    survey_defect_id=new_survey_defect.id,
                )
                await self.repo.session.refresh(
                    instance=new_survey_defect, attribute_names=["photos"]
                )
            return new_survey_defect
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyDefectCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY_DEFECT}: {e}"
            )

    async def update_defect(
        self,
        obj_in: SurveyDefectUpdate,
        defect_db: SurveyDefect,
    ) -> SurveyDefect:
        """Обновляет данные существующего дефекта."""
        try:
            defect = await self.update_obj(db_obj=defect_db, obj_in=obj_in)
            return defect
        except Exception as e:
            raise SurveyDefectUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(self, defect_db: SurveyDefect) -> list[Path]:
        """Подготавливает дефект и связанные фотографии к удалению."""
        paths_photo_to_delete = []
        for photo in defect_db.photos:
            paths_defect_photo = await self.photo_service._stage_deletion(
                photo_id=photo.id
            )
            paths_photo_to_delete.extend(paths_defect_photo)
        await self.repo.remove(id=defect_db.id)
        return paths_photo_to_delete

    async def delete_with_photos(self, defect_db: SurveyDefect) -> None:
        """
        Удаляет дефект, связанные фотографии и записи в БД.
        """
        try:
            async with atomic_transaction(session=self.repo.session):
                paths_photo_to_delete = await self._stage_deletion(
                    defect_db=defect_db
                )
            if paths_photo_to_delete:
                for path in paths_photo_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except Exception as e:
            raise SurveyDefectRemovingError(
                f"{ExceptionDetails.FAILED_ROMOVE_SURVEY_DEFECT}: {e}"
            ) from e
