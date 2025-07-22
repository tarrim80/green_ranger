import os
from pathlib import Path

from fastapi import Depends, UploadFile

from app.core.constants import ExceptionDetails
from app.core.exceptions import (
    NotFoundError,
    SurveyDefectCreationError,
    SurveyDefectRemovingError,
    SurveyDefectUpdatingError,
)
from app.core.transaction_manager import atomic_transaction
from app.models import Photo, SurveyDefect
from app.repositories.survey_defect import SurveyDefectRepository
from app.schemas import SurveyDefectCreate, SurveyDefectUpdate
from app.services.mixins.base_update import UpdateObjMixin
from app.services.photo_service import PhotoService
from app.utils.photo_uploader import save_uploaded_images


class SurveyDefectService(UpdateObjMixin):
    def __init__(
        self,
        repo: SurveyDefectRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def get_all_defects(self) -> list[SurveyDefect]:
        defects_db = await self.repo.get_multi()
        return list(defects_db)

    async def get_defect(self, obj_id: int) -> SurveyDefect:
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
        defects_db = await self.repo.get_all_by_survey_id(survey_id=survey_id)
        return list(defects_db)

    async def create_with_photos(
        self,
        survey_defect_in: SurveyDefectCreate,
        files: list[UploadFile],
    ) -> SurveyDefect:
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
                for photo_data in photos_data:
                    new_data = {
                        "file_path": photo_data["file_path"],
                        "survey_defect_id": new_survey_defect.id,
                    }
                    new_photo = Photo(**new_data)
                    self.repo.session.add(instance=new_photo)
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
        self, obj_id: int, obj_in: SurveyDefectUpdate
    ) -> SurveyDefect:
        try:
            defect_db = await self.repo.get(id=obj_id)
            if not defect_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            defect = await self.update_obj(db_obj=defect_db, obj_in=obj_in)
            return defect
        except NotFoundError:
            raise
        except Exception as e:
            raise SurveyDefectUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def _stage_deletion(self, defect_id: int) -> list[Path]:
        defect_db = await self.repo.get(id=defect_id)
        if not defect_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(), id=defect_id
                )
            )
        photos_to_delete: list[Path] = []
        for photo in defect_db.photos:
            photo_path = await self.photo_service._stage_deletion(
                photo_id=photo.id
            )
            photos_to_delete.append(photo_path)
        await self.repo.remove(id=defect_id)
        return photos_to_delete

    async def delete_with_photos(self, defect_id: int) -> None:
        try:
            async with atomic_transaction(session=self.repo.session):
                photos_to_delete = await self._stage_deletion(
                    defect_id=defect_id
                )
            if photos_to_delete:
                for path in photos_to_delete:
                    if os.path.exists(path=path):
                        os.remove(path=path)
        except NotFoundError:
            raise
        except Exception as e:
            raise SurveyDefectRemovingError(
                f"{ExceptionDetails.FAILED_ROMOVE_SURVEY_DEFECT}: {e}"
            ) from e
