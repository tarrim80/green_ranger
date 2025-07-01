from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails, ValidationMessages
from app.core.exceptions import (
    NotFoundError,
    PhotoCreationError,
    PhotoRemovingError,
)
from app.repositories import PhotoRepository
from app.schemas import PhotoRead, PhotoUpdate
from app.services.photo_service import PhotoService

router = APIRouter()


@router.post(
    path="/upload",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка одной или нескольких фотографий",
    description="Принимает один или несколько файлов и сохраняет их.",
)
async def upload_photos(
    files: list[UploadFile] = File(default=...),
    defect_type_id: int | None = Form(
        default=None, json_schema_extra={"example": 1, "default": None}
    ),
    survey_id: int | None = Form(
        default=None, json_schema_extra={"example": 1, "default": None}
    ),
    survey_defect_id: int | None = Form(
        default=None, json_schema_extra={"example": 1, "default": None}
    ),
    service: PhotoService = Depends(),
) -> list[PhotoRead]:
    try:
        photos = await service.upload_and_link_photos(
            files=files,
            defect_type_id=defect_type_id,
            survey_id=survey_id,
            survey_defect_id=survey_defect_id,
        )
        return [PhotoRead.model_validate(photo) for photo in photos]
    except PhotoCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_CREATE_PHOTO} {e}",
        )


@router.patch(
    path="/{photo_id}",
    response_model=PhotoRead,
    summary="Изменение фотографии",
    description="Изменяет связи фотографии.",
)
async def photo_update(
    photo_id: int, photo_in: PhotoUpdate, repo: PhotoRepository = Depends()
) -> PhotoRead:
    photo_db = await repo.get(id=photo_id)
    if not photo_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Фото"),
        )
    try:
        updated_photo = await repo.update(db_obj=photo_db, obj_in=photo_in)
        return PhotoRead.model_validate(obj=updated_photo)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    path="/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление фото",
    description="Удаляет фото и запись в БД по его идентификатору (id).",
)
async def photo_delete(
    photo_id: int, service: PhotoService = Depends()
) -> None:
    try:
        await service.delete_photo_file(photo_id=photo_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Фото"),
        )
    except PhotoRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}",
        )
