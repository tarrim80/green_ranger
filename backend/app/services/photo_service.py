import os

from fastapi import Depends, UploadFile

from app.core.constants import ExceptionDetails
from app.core.exceptions import (
    NotFoundError,
    PhotoCreationError,
    PhotoRemovingError,
)
from app.models import Photo
from app.repositories.photo import PhotoRepository
from app.schemas import PhotoCreate
from app.services.photo_filename import MEDIA_ROOT
from app.services.photo_uploader import save_uploaded_images


class PhotoService:
    def __init__(self, repo: PhotoRepository = Depends()) -> None:
        self.repo = repo

    async def upload_and_link_photos(
        self,
        files: list[UploadFile],
        defect_type_id: int | None = None,
        survey_id: int | None = None,
        survey_defect_id: int | None = None,
    ) -> list[Photo]:
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
            photos_db = await self.repo.create_many(objs_in=photos_to_create)
            return photos_db
        except Exception as e:
            await self.repo.session.rollback()
            for filename in saved_file_paths:
                os.remove(path=filename)
            raise PhotoCreationError(
                f"{ExceptionDetails.FAILED_CREATE_PHOTO}: {e}"
            )

    async def delete_photo_file(self, photo_id: int) -> None:
        try:
            photo_db = await self.repo.get(id=photo_id)
            if not photo_db:
                raise NotFoundError
            await self.repo.remove(id=photo_id)

            file_to_delete = MEDIA_ROOT / photo_db.file_path
            if os.path.exists(path=file_to_delete):
                os.remove(path=file_to_delete)
        except Exception as e:
            raise PhotoRemovingError(e)
