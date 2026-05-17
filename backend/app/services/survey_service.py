import os
from operator import attrgetter
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
    SurveyCreationError,
    SurveyRemovingError,
    SurveyUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Survey
from app.repositories.survey import SurveyRepository
from app.schemas import SurveyCreate, SurveyStatusEnum, SurveyUpdate
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService
from app.services.tree_service import TreeService
from app.utils.photo_uploader import save_uploaded_images

TRANSIENT_STATUSES = (
    SurveyStatusEnum.ON_REVIEW,
    SurveyStatusEnum.NEEDS_CORRECTION,
)


class SurveyService:
    """Сервисный слой для управления обследованиями."""

    def __init__(
        self,
        repo: SurveyRepository = Depends(),
        tree_service: TreeService = Depends(),
        defect_service: SurveyDefectService = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.tree_service = tree_service
        self.defect_service = defect_service
        self.photo_service = photo_service

    async def get_all_surveys(
        self,
    ) -> list[Survey]:
        """Получает список всех обследований."""
        surveys_db = await self.repo.get_multi()
        return list(surveys_db)

    async def get_surveys_by_tree_id(self, tree_id: int) -> list[Survey]:
        """Получает все обследования для конкретного растения."""
        surveys_db = await self.repo.get_all_by_tree_id(tree_id=tree_id)
        return list(surveys_db)

    async def create_with_photos(
        self,
        survey_in: SurveyCreate,
        files: list[UploadFile],
    ) -> Survey:
        """Создает новое обследование с привязкой фотографий."""
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = survey_in.model_dump()
            new_survey = Survey(**new_data)
            async with atomic_transaction(session=self.repo.session):
                self.repo.session.add(instance=new_survey)
                await self.repo.session.flush()
                await self.photo_service.create_photo_batch(
                    photos_data=photos_data, survey_id=new_survey.id
                )
                await self.repo.session.refresh(
                    instance=new_survey,
                    attribute_names=[
                        "tree_photos",
                        "survey_defects",
                        "author",
                    ],
                )
            return new_survey
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY}: {e}"
            )

    async def update_survey_with_photos(
        self,
        survey_db: Survey,
        obj_in: SurveyUpdate,
        files: list[UploadFile] | None,
    ) -> Survey:
        """
        Обновляет данные существующего обследования.
        """
        saved_file_paths = []
        photos_data = []
        try:
            await self._validate_survey_not_completed(survey_db=survey_db)
            if files:
                photos_data, saved_file_paths = await save_uploaded_images(
                    files=files
                )
            update_data = obj_in.model_dump(exclude_unset=True)
            new_status = obj_in.survey_status
            await self._validate_status_transition(
                survey_db=survey_db, new_status=new_status
            )

            async with atomic_transaction(session=self.repo.session):
                for field, value in update_data.items():
                    setattr(survey_db, field, value)
                self.repo.session.add(instance=survey_db)

                await self.tree_service.sync_state_tree_with_last_survey(
                    tree=survey_db.tree, survey=survey_db
                )

                await self.repo.session.flush()
                await self.photo_service.create_photo_batch(
                    photos_data=photos_data, survey_id=survey_db.id
                )
                await self.repo.session.refresh(
                    instance=survey_db,
                    attribute_names=[
                        "tree_photos",
                        "survey_defects",
                        "author",
                        "updated_at",
                    ],
                )
            return survey_db
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _validate_survey_not_completed(self, survey_db) -> None:
        """Проверяет обследование на завершённость."""
        if survey_db.survey_status not in TRANSIENT_STATUSES:
            raise NotAllowedError(
                ExceptionDetails.CANNOT_UPDATE_COMPLETED_SURVEYS
            )

    async def _validate_status_transition(
        self, survey_db: Survey, new_status: SurveyStatusEnum | None
    ) -> None:
        """Проверяет возможность изменения статуса обследования."""
        if not new_status:
            return
        all_surveys = sorted(
            survey_db.tree.surveys, key=attrgetter("created_at")
        )
        current_index = all_surveys.index(survey_db)
        if new_status == SurveyStatusEnum.APPROVED:
            previous_surveys = all_surveys[:current_index]
            if any(
                s.survey_status in TRANSIENT_STATUSES for s in previous_surveys
            ):
                raise NotAllowedError(
                    ExceptionDetails.PREVIOUS_SURVEYS_NOT_COMPLETED
                )
        if new_status in TRANSIENT_STATUSES:
            is_last = current_index == len(all_surveys) - 1
            if not is_last:
                raise NotAllowedError(
                    ExceptionDetails.CANNOT_RESET_STATUS_FOR_OLD_SURVEY
                )

    async def _stage_deletion(self, survey_db: Survey) -> list[Path]:
        """
        Подготавливает обследование и все связанные с ним данные к удалению.
        """
        paths_photo_to_delete = []
        for survey_defect in survey_db.survey_defects:
            path_defect_photo_to_delete = (
                await self.defect_service._stage_deletion(
                    defect_db=survey_defect
                )
            )
            if path_defect_photo_to_delete:
                paths_photo_to_delete.extend(path_defect_photo_to_delete)
        for tree_photo in survey_db.tree_photos:
            paths_tree_photo_to_delete = (
                await self.photo_service._stage_deletion(photo=tree_photo)
            )
            paths_photo_to_delete.extend(paths_tree_photo_to_delete)
        await self.repo.remove(id=survey_db.id)
        return paths_photo_to_delete

    async def delete_with_photos(self, survey_db: Survey) -> None:
        """
        Удаляет обследование и все связанные с ним данные.
        """
        try:
            async with atomic_transaction(session=self.repo.session):
                paths_photo_to_delete = await self._stage_deletion(
                    survey_db=survey_db
                )
            if paths_photo_to_delete:
                for path in paths_photo_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except Exception as e:
            raise SurveyRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_SURVEY}: {e}"
            ) from e
