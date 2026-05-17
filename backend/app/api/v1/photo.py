from fastapi import Depends, File, Form, UploadFile, status
from fastapi.routing import APIRouter

from app.api.v1.dependencies import (
    check_photo_deletion_access,
    check_photo_uploading_access,
    get_photo_db,
)
from app.core.exceptions import (
    ExceptionDetails,
    NotAllowedError,
)
from app.core.permissions import (
    IsVolunteer,
    permission_dependency,
)
from app.models import Photo
from app.schemas import PhotoRead
from app.services.photo_service import PhotoService

router = APIRouter()


@router.post(
    path="/upload",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка одной или нескольких фотографий",
    description="Принимает один или несколько файлов и сохраняет их.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_photo_uploading_access),
    ],
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
    provided_ids = [
        id_
        for id_ in [defect_type_id, survey_id, survey_defect_id]
        if id_ is not None
    ]
    if len(provided_ids) != 1:
        raise NotAllowedError(ExceptionDetails.REQUIRED_EXACTLY_ONE_LINK_ID)

    photos = await service.upload_and_link_photos(
        files=files,
        defect_type_id=defect_type_id,
        survey_id=survey_id,
        survey_defect_id=survey_defect_id,
    )
    return [PhotoRead.model_validate(photo) for photo in photos]


@router.delete(
    path="/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление фото",
    description="Удаляет фото и запись в БД по его идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_photo_deletion_access),
    ],
)
async def delete_photo(
    service: PhotoService = Depends(),
    photo_db: Photo = Depends(dependency=get_photo_db),
) -> None:
    await service.delete_photo(photo=photo_db)
