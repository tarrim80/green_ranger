import os

from fastapi import Depends, UploadFile

from app.core.constants import ExceptionDetails
from app.core.exceptions import SurveyDefectCreationError
from app.models import Photo, SurveyDefect
from app.repositories.survey_defect import SurveyDefectRepository
from app.services.photo_service import PhotoService
from app.utils.photo_uploader import save_uploaded_images


class SurveyDefectService:
    def __init__(
        self,
        repo: SurveyDefectRepository = Depends(),
        photo_service: PhotoService = Depends(),
    ) -> None:
        self.repo = repo
        self.photo_service = photo_service

    async def create_defect_with_photos(
        self,
        survey_id: int,
        defect_type_id: int,
        description: str | None,
        files: list[UploadFile],
    ) -> SurveyDefect:
        saved_file_paths = []
        try:
            photos_data, saved_file_paths = await save_uploaded_images(
                files=files
            )
            new_data = {
                "survey_id": survey_id,
                "defect_type_id": defect_type_id,
                "description": description,
            }
            new_survey_defect = SurveyDefect(**new_data)
            self.repo.session.add(instance=new_survey_defect)
            await self.repo.session.flush()
            for photo_data in photos_data:
                new_data = {
                    "file_path": photo_data["file_path"],
                    "survey_defect_id": new_survey_defect.id,
                }
                new_photo = Photo(**new_data)
                self.repo.session.add(instance=new_photo)
            await self.repo.session.commit()
            await self.repo.session.refresh(
                instance=new_survey_defect, attribute_names=["photos"]
            )
            return new_survey_defect
        except Exception as e:
            await self.repo.session.rollback()
            for filename in saved_file_paths:
                os.remove(filename)
            raise SurveyDefectCreationError(
                f"{ExceptionDetails.FAILED_CREATE_SURVEY_DEFECT}: {e}"
            )

    async def delete_with_photos(self, defect_id: int) -> None | SurveyDefect:
        defect_db = await self.repo.get(id=defect_id)
        if not defect_db:
            return None
        for photo in defect_db.photos:
            await self.photo_service.delete_photo_file(photo_id=photo.id)
        return await self.repo.remove(id=defect_id)
