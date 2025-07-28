from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PhotoCreationError,
    SurveyDefectCreationError,
    SurveyDefectRemovingError,
    SurveyDefectUpdatingError,
)
from app.core.permissions import IsCurator, IsVolunteer, permission_dependency
from app.schemas import (
    DefectStatusEnum,
    PhotoRead,
    SurveyDefectCreate,
    SurveyDefectRead,
    SurveyDefectUpdate,
)
from app.schemas.defaults import SurveyDefectDefaults
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService

router = APIRouter()


@router.get(
    path="/defects/",
    response_model=list[SurveyDefectRead],
    summary="Получение списка всех дефектов",
    description="Показывает список всех обнаруженных дефектов.",
)
async def get_all_survey_defects(
    service: SurveyDefectService = Depends(),
) -> list[SurveyDefectRead]:
    defects_db = await service.get_all_defects()
    return [
        SurveyDefectRead.model_validate(obj=defect_db)
        for defect_db in defects_db
    ]


@router.get(
    path="/defects/{defect_id}",
    response_model=SurveyDefectRead,
    status_code=status.HTTP_200_OK,
    summary="Получение конкретного дефекта",
    description="Показывает конкретный дефект по идентификатору (id).",
)
async def get_survey_defect(
    defect_id: int, service: SurveyDefectService = Depends()
) -> SurveyDefectRead:
    try:
        defect_db = await service.get_defect(obj_id=defect_id)
        return SurveyDefectRead.model_validate(obj=defect_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.get(
    path="/surveys/{survey_id}/defects",
    response_model=list[SurveyDefectRead],
    status_code=status.HTTP_200_OK,
    summary="Получение всех дефектов в обследовании",
    description="Показывает список всех дефектов обнаруженных и/или \
        отредактированных в обследовании с определенным идентификатором (id).",
)
async def get_survey_defects_by_survey_id(
    survey_id: int, service: SurveyDefectService = Depends()
) -> list[SurveyDefectRead]:
    defects_db = await service.get_defects_by_survey_id(survey_id=survey_id)
    return [
        SurveyDefectRead.model_validate(obj=defect_db)
        for defect_db in defects_db
    ]


@router.post(
    path="/surveys/{survey_id}/defects",
    response_model=SurveyDefectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового обнаруженного дефекта",
    description="Создает новый обнаруженный дефект.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
)
async def create_defect(
    survey_id: int,
    defect_type_id: int = Form(default=...),
    description: str | None = Form(default=None),
    defect_status: DefectStatusEnum = SurveyDefectDefaults.DEFECT_STATUS,
    files: list[UploadFile] = File(default=...),
    service: SurveyDefectService = Depends(),
) -> SurveyDefectRead:
    survey_defect_in = SurveyDefectCreate(
        survey_id=survey_id,
        defect_type_id=defect_type_id,
        description=description,
        defect_status=defect_status,
    )
    try:
        survey_defect_db = await service.create_with_photos(
            survey_defect_in=survey_defect_in,
            files=files,
        )
        return SurveyDefectRead.model_validate(obj=survey_defect_db)
    except SurveyDefectCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    path="/defects/{defect_id}/photos",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавление фотографий к дефекту",
    description="Загружает одну или несколько фотографий \
        и привязывает их к существующему дефекту.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
)
async def add_photos_to_defect(
    defect_id: int, files: list[UploadFile], service: PhotoService = Depends()
) -> list[PhotoRead]:
    try:
        photos = await service.upload_and_link_photos(
            files=files,
            survey_defect_id=defect_id,
        )
        return [PhotoRead.model_validate(photo) for photo in photos]
    except PhotoCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_CREATE_PHOTO} {e}",
        )


@router.patch(
    path="/defects/{defect_id}",
    response_model=SurveyDefectRead,
    summary="Изменение обнаруженного дефекта",
    description="Изменяет поля записи дефекта по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def update_defect(
    defect_id: int,
    defect_in: SurveyDefectUpdate,
    service: SurveyDefectService = Depends(),
) -> SurveyDefectRead:
    try:
        defect_update_db = await service.update_defect(
            obj_id=defect_id, obj_in=defect_in
        )
        return SurveyDefectRead.model_validate(obj=defect_update_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except SurveyDefectUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete(
    path="/defects/{defect_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление конкретного дефекта",
    description="Удаляет дефект по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def delete_defect(
    defect_id: int, service: SurveyDefectService = Depends()
) -> None:
    try:
        await service.delete_with_photos(defect_id=defect_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except SurveyDefectRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
