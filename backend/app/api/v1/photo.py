from fastapi import Depends, File, Form, HTTPException, UploadFile, status
from fastapi.routing import APIRouter

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
    PhotoCreationError,
    PhotoRemovingError,
)
from app.core.permissions import (
    IsAdmin,
    IsSurveyDefectOwnerOrCurator,
    IsSurveyOwnerOrCurator,
    IsCurator,
    IsVolunteer,
    permission_dependency,
)
from app.core.user import current_user
from app.models import User
from app.schemas import PhotoRead
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService
from app.services.survey_service import SurveyService
from app.repositories.survey import SurveyRepository
from app.repositories.survey_defect import SurveyDefectRepository

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
    survey_repo: SurveyRepository = Depends(),
    defect_repo: SurveyDefectRepository = Depends(),
) -> list[PhotoRead]:
    provided_ids = [
        id_
        for id_ in [defect_type_id, survey_id, survey_defect_id]
        if id_ is not None
    ]
    if len(provided_ids) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ExceptionDetails.REQUIRED_EXACTLY_ONE_LINK_ID,
        )

    try:
        if defect_type_id:
            permission = await IsAdmin().has_permission(user=current_user)
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )

        if survey_id:
            survey = await survey_repo.get(id=survey_id)
            if not survey:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=survey_repo.model.verbose_name(),
                        id=survey_id,
                    )
                )
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=current_user, obj=survey
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )

        if survey_defect_id:
            survey_defect = await defect_repo.get(id=survey_defect_id)
            if not survey_defect:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=defect_repo.model.verbose_name(),
                        id=survey_defect_id,
                    )
                )
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=current_user, obj=survey_defect
                )
            )
            if not permission:
                raise PermissionDenniedError(
                    ExceptionDetails.NO_RIGHT_FOR_ACTION
                )

        photos = await service.upload_and_link_photos(
            files=files,
            defect_type_id=defect_type_id,
            survey_id=survey_id,
            survey_defect_id=survey_defect_id,
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
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
)
async def delete_photo(
    photo_id: int,
    service: PhotoService = Depends(),
    current_user: User = Depends(dependency=current_user),
) -> None:
    try:
        photo_db = await service.repo.get(id=photo_id)
        if not photo_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=service.repo.model.verbose_name(),
                    id=photo_id,
                )
            )

        if photo_db.defect_type_id:
            permission = await IsAdmin().has_permission(user=current_user)
        elif photo_db.tree_photo:
            permission = await IsSurveyOwnerOrCurator().has_obj_permission(
                user=current_user, obj=photo_db.tree_photo
            )
        elif photo_db.survey_defect_photo:
            permission = (
                await IsSurveyDefectOwnerOrCurator().has_obj_permission(
                    user=current_user, obj=photo_db.survey_defect_photo
                )
            )
        else:
            permission = await IsAdmin().has_permission(user=current_user)

        if not permission:
            raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)

        await service.delete_photo(photo_id=photo_id)

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
