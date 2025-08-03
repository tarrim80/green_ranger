import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
    SurveyCreationError,
    SurveyRemovingError,
    SurveyUpdatingError,
)
from app.core.permissions import IsSurveyOwnerOrCurator
from app.core.transaction_manager import atomic_transaction
from app.models import Photo, Survey, User
from app.repositories.survey import SurveyRepository
from app.schemas import SurveyCreate, SurveyUpdate
from app.services.mixins import UpdateObjMixin
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService
from app.utils.photo_uploader import save_uploaded_images


class SurveyService(UpdateObjMixin):
    """Сервисный слой для управления обследованиями."""

    def __init__(
        self,
        repo: SurveyRepository = Depends(),
        defect_service: SurveyDefectService = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.defect_service = defect_service
        self.photo_service = photo_service

    async def get_all_surveys(
        self,
    ) -> list[Survey]:
        """Получает список всех обследований."""
        surveys_db = await self.repo.get_multi()
        return list(surveys_db)

    async def get_survey(self, obj_id: int) -> Survey:
        """Получает обследование по его идентификатору."""
        survey_db = await self.repo.get(id=obj_id)
        if not survey_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return survey_db

    async def get_surveys_by_tree_id(self, tree_id: int) -> list[Survey]:
        """Получает все обследования для конкретного растения."""
        surveys_db = await self.repo.get_all_by_tree_id(tree_id=tree_id)
        return list(surveys_db)

    async def create_with_photos(
        self, survey_in: SurveyCreate, files: list[UploadFile]
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
                for photo_data in photos_data:
                    new_data = {
                        "file_path": photo_data["file_path"],
                        "survey_id": new_survey.id,
                    }
                    new_photo = Photo(**new_data)
                    self.repo.session.add(instance=new_photo)
                await self.repo.session.refresh(
                    instance=new_survey, attribute_names=["tree_photos"]
                )
            return new_survey
        except Exception as e:
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY}: {e}"
            )

    async def update_survey(
        self, obj_id: int, obj_in: SurveyUpdate, user: User
    ) -> Survey:
        """
        Обновляет данные существующего обследования с проверкой прав доступа.
        """
        try:
            survey_db = await self.repo.get(id=obj_id)
            if not survey_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=user, obj=survey_db
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            survey = await self.update_obj(db_obj=survey_db, obj_in=obj_in)
            return survey
        except NotFoundError:
            raise
        except PermissionDenniedError:
            raise
        except Exception as e:
            raise SurveyUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(self, survey_db: Survey) -> list[Path]:
        """
        Подготавливает обследование и все связанные с ним данные к удалению.
        """
        photos_to_delete = []
        for survey_defect in survey_db.survey_defects:
            defect_photos_to_delete = (
                await self.defect_service._stage_deletion(
                    defect_db=survey_defect
                )
            )
            if defect_photos_to_delete:
                photos_to_delete.extend(defect_photos_to_delete)
        for tree_photo in survey_db.tree_photos:
            tree_photo_to_delete = await self.photo_service._stage_deletion(
                photo_id=tree_photo.id
            )
            photos_to_delete.append(tree_photo_to_delete)
        await self.repo.remove(id=survey_db.id)
        return photos_to_delete

    async def delete_with_photos(self, survey_id: int, user: User) -> None:
        """
        Удаляет обследование и все связанные с ним данные с проверкой прав.
        """
        try:
            survey_db = await self.repo.get(id=survey_id)
            if not survey_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(), id=survey_id
                    )
                )
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=user, obj=survey_db
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )
            async with atomic_transaction(session=self.repo.session):
                photos_to_delete = await self._stage_deletion(
                    survey_db=survey_db
                )
            if photos_to_delete:
                for path in photos_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except NotFoundError:
            raise
        except PermissionDenniedError:
            raise
        except Exception as e:
            raise SurveyRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_SURVEY}: {e}"
            ) from e
