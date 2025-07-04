from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.constants import ExceptionDetails, SurveyDefectDefaults
from app.core.exceptions import PhotoCreationError, SurveyDefectCreationError
from app.repositories.survey_defect import SurveyDefectRepository
from app.schemas import (
    DefectStatusEnum,
    PhotoRead,
    SurveyDefectRead,
    SurveyDefectUpdate,
)
from app.services.photo_service import PhotoService
from app.services.survey_defect_service import SurveyDefectService

router = APIRouter()


@router.get(
    path="/defects/{defect_id}",
    response_model=SurveyDefectRead,
    status_code=status.HTTP_200_OK,
    summary="Получение конкретного дефекта",
    description="Показывает конкретный дефект по идентификатору (id).",
)
async def get_defect(
    defect_id: int, repo: SurveyDefectRepository = Depends()
) -> SurveyDefectRead:
    survey_defect_db = await repo.get(id=defect_id)
    if not survey_defect_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Дефект"),
        )
    return SurveyDefectRead.model_validate(obj=survey_defect_db)


@router.get(
    path="/surveys/{survey_id}/defects",
    response_model=list[SurveyDefectRead],
    status_code=status.HTTP_200_OK,
    summary="Получение всех дефектов в обследовании",
    description="Показывает список всех дефектов обнаруженных и/или \
        отредактированных в обследовании с определенным идентификатором (id).",
)
async def get_defects_by_survey_id(
    survey_id: int, repo: SurveyDefectRepository = Depends()
) -> list[SurveyDefectRead]:
    defects_db = await repo.get_all_by_survey_id(survey_id=survey_id)
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
)
async def create_defect(
    survey_id: int,
    defect_type_id: int = Form(default=...),
    description: str | None = Form(default=None),
    defect_status: DefectStatusEnum = SurveyDefectDefaults.DEFECT_STATUS,
    files: list[UploadFile] = File(default=...),
    service: SurveyDefectService = Depends(),
) -> SurveyDefectRead:
    try:
        survey_defect_db = await service.create_defect_with_photos(
            survey_id=survey_id,
            defect_type_id=defect_type_id,
            description=description,
            defect_status=defect_status,
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
)
async def update_defect(
    defect_id: int,
    defect_in: SurveyDefectUpdate,
    repo: SurveyDefectRepository = Depends(),
) -> SurveyDefectRead:
    defect_db = await repo.get(id=defect_id)
    if not defect_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Дефект"),
        )
    defect_update_db = await repo.update(db_obj=defect_db, obj_in=defect_in)
    return SurveyDefectRead.model_validate(obj=defect_update_db)


@router.delete(
    path="/defects/{defect_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление конкретного дефекта",
    description="Удаляет дефект по идентификатору (id).",
)
async def delete_defect(
    defect_id: int, service: SurveyDefectService = Depends()
) -> None:
    if not await service.delete_with_photos(defect_id=defect_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Дефект"),
        )
