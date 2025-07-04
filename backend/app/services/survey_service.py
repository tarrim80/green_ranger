import os

from fastapi import Depends, UploadFile

from app.core.constants import ExceptionDetails
from app.core.exceptions import SurveyCreationError
from app.models import Photo, Survey
from app.repositories.survey import SurveyRepository
from app.schemas import SurveyCreate
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService
from app.utils.photo_uploader import save_uploaded_images


class SurveyService:
    def __init__(
        self,
        repo: SurveyRepository = Depends(),
        defect_service: SurveyDefectService = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.defect_service = defect_service
        self.photo_service = photo_service

    async def create_with_photos(
        self, survey_in: SurveyCreate, files: list[UploadFile]
    ) -> Survey:
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = survey_in.model_dump()
            new_survey = Survey(**new_data)
            self.repo.session.add(instance=new_survey)
            await self.repo.session.flush()
            for photo_data in photos_data:
                new_data = {
                    "file_path": photo_data["file_path"],
                    "survey_id": new_survey.id,
                }
                new_photo = Photo(**new_data)
                self.repo.session.add(instance=new_photo)
            await self.repo.session.commit()
            await self.repo.session.refresh(
                instance=new_survey, attribute_names=["tree_photos"]
            )
            return new_survey
        except Exception as e:
            await self.repo.session.rollback()
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY}: {e}"
            )

    async def delete_with_photos(self, survey_id: int) -> None | Survey:
        survey_db = await self.repo.get(id=survey_id)
        if not survey_db:
            return None
        for survey_defect in survey_db.survey_defects:
            await self.defect_service.delete_with_photos(
                defect_id=survey_defect.id
            )
        for tree_photo in survey_db.tree_photos:
            await self.photo_service.delete_photo_file(photo_id=tree_photo.id)
        return await self.repo.remove(id=survey_id)
