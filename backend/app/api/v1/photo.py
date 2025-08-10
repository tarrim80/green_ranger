from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.routing import APIRouter

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
    PhotoCreationError,
    PhotoRemovingError,
)
from app.core.permissions import IsCurator, IsVolunteer, permission_dependency
from app.core.user import current_user
from app.models import User
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
        Depends(dependency=permission_dependency(permission=IsVolunteer))
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
    current_user: User = Depends(dependency=current_user),
) -> list[PhotoRead]:
    try:
        photos = await service.upload_and_link_photos(
            files=files,
            defect_type_id=defect_type_id,
            survey_id=survey_id,
            survey_defect_id=survey_defect_id,
            user=current_user,
        )
        return [PhotoRead.model_validate(photo) for photo in photos]
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except PermissionDenniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e
    except PhotoCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_CREATE_PHOTO} {e}",
        )


@router.delete(
    path="/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление фото",
    description="Удаляет фото и запись в БД по его идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def delete_photo(
    photo_id: int,
    service: PhotoService = Depends(),
    current_user: User = Depends(dependency=current_user),
) -> None:
    try:
        await service.delete_photo(photo_id=photo_id, user=current_user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except PermissionDenniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e
    except PhotoRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
