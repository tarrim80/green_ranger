from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)

from app.api.v1.dependencies import (
    check_survey_defect_modification_access,
    check_survey_modification_access,
    get_survey_db,
    get_survey_defect_db,
)
from app.core.permissions import (
    IsCurator,
    IsVolunteer,
    permission_dependency,
)
from app.models import Survey
from app.models.survey_defect import SurveyDefect
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
    defect: SurveyDefect = Depends(dependency=get_survey_defect_db),
) -> SurveyDefectRead:
    return SurveyDefectRead.model_validate(obj=defect)


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
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_survey_modification_access),
    ],
)
async def create_defect(
    survey_db: Survey = Depends(dependency=get_survey_db),
    defect_type_id: int = Form(default=...),
    description: str | None = Form(default=None),
    defect_status: DefectStatusEnum = SurveyDefectDefaults.DEFECT_STATUS,
    files: list[UploadFile] = File(default=...),
    service: SurveyDefectService = Depends(),
) -> SurveyDefectRead:
    survey_defect_in = SurveyDefectCreate(
        survey_id=survey_db.id,
        defect_type_id=defect_type_id,
        description=description,
        defect_status=defect_status,
    )
    survey_defect_db = await service.create_with_photos(
        survey_defect_in=survey_defect_in, files=files
    )
    return SurveyDefectRead.model_validate(obj=survey_defect_db)


@router.post(
    path="/defects/{defect_id}/photos",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавление фотографий к дефекту",
    description="Загружает одну или несколько фотографий \
        и привязывает их к существующему дефекту.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_survey_defect_modification_access),
    ],
)
async def add_photos_to_defect(
    files: list[UploadFile],
    defect: SurveyDefect = Depends(dependency=get_survey_defect_db),
    service: PhotoService = Depends(),
) -> list[PhotoRead]:
    photos = await service.upload_and_link_photos(
        files=files,
        survey_defect_id=defect.id,
    )
    return [PhotoRead.model_validate(photo) for photo in photos]


@router.patch(
    path="/defects/{defect_id}",
    response_model=SurveyDefectRead,
    summary="Изменение обнаруженного дефекта",
    description="Изменяет поля записи дефекта по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_survey_defect_modification_access),
    ],
)
async def update_defect(
    defect_in: SurveyDefectUpdate,
    defect_db: SurveyDefect = Depends(dependency=get_survey_defect_db),
    service: SurveyDefectService = Depends(),
) -> SurveyDefectRead:
    defect_update_db = await service.update_defect(
        obj_in=defect_in,
        defect_db=defect_db,
    )
    return SurveyDefectRead.model_validate(obj=defect_update_db)


@router.delete(
    path="/defects/{defect_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление конкретного дефекта",
    description="Удаляет дефект по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator)),
        Depends(dependency=check_survey_defect_modification_access),
    ],
)
async def delete_defect(
    defect_db: SurveyDefect = Depends(dependency=get_survey_defect_db),
    service: SurveyDefectService = Depends(),
) -> None:
    await service.delete_with_photos(defect_db=defect_db)
