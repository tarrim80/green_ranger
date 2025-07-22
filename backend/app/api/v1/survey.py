from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from app.core.constants import ExceptionDetails, SurveyDefaults
from app.core.exceptions import (
    NotFoundError,
    PhotoCreationError,
    SurveyCreationError,
    SurveyRemovingError,
    SurveyUpdatingError,
)
from app.core.user import current_user
from app.models import User
from app.schemas import (
    PhotoRead,
    SurveyCreate,
    SurveyRead,
    SurveyUpdate,
    TreeConditionEnum,
)
from app.services.photo_service import PhotoService
from app.services.survey_service import SurveyService

router = APIRouter()


@router.get(
    path="/surveys",
    response_model=list[SurveyRead],
    summary="Получение списка обследований",
    description="Показывает список всех обследований зарегистрированных \
        в приложении.",
)
async def get_all_surveys(
    service: SurveyService = Depends(),
) -> list[SurveyRead]:
    surveys_db = await service.get_all_surveys()
    return [
        SurveyRead.model_validate(obj=survey_db) for survey_db in surveys_db
    ]


@router.get(
    path="/surveys/{survey_id}",
    response_model=SurveyRead,
    status_code=status.HTTP_200_OK,
    summary="Получение обследования",
    description="Показывает обследование по идентификатору (id).",
)
async def get_survey(
    survey_id: int, service: SurveyService = Depends()
) -> SurveyRead:
    try:
        survey_db = await service.get_survey(obj_id=survey_id)
        return SurveyRead.model_validate(obj=survey_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.get(
    path="/trees/{tree_id}/surveys",
    response_model=list[SurveyRead],
    status_code=status.HTTP_200_OK,
    summary="Получение всех обследований растения",
    description="Показывает список всех обследований растения \
        с определенным идентификатором (id).",
)
async def get_surveys_by_tree_id(
    tree_id: int, service: SurveyService = Depends()
) -> list[SurveyRead]:
    surveys_db = await service.get_surveys_by_tree_id(tree_id=tree_id)
    return [
        SurveyRead.model_validate(obj=survey_db) for survey_db in surveys_db
    ]


@router.post(
    path="/surveys",
    response_model=SurveyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового обследования",
    description="Создает новое обследование растения.",
)
async def create_survey(
    tree_id: int = Form(default=...),
    age: int | None = Form(default=None),
    height: float | None = Form(default=None),
    diameter: float | None = Form(default=None),
    trunk_count: int = Form(default=SurveyDefaults.TRUNK_COUNT),
    condition: TreeConditionEnum = Form(default=SurveyDefaults.CONDITION),
    is_emergency_report: bool = Form(
        default=SurveyDefaults.IS_EMERGENCY_REPORT
    ),
    note: str | None = Form(default=None),
    files: list[UploadFile] = File(default=...),
    current_user: User = Depends(dependency=current_user),
    service: SurveyService = Depends(),
) -> SurveyRead:
    survey_in = SurveyCreate(
        tree_id=tree_id,
        age=age,
        height=height,
        diameter=diameter,
        trunk_count=trunk_count,
        condition=condition,
        is_emergency_report=is_emergency_report,
        note=note,
        author_id=current_user.id,
    )
    try:
        survey_db = await service.create_with_photos(
            survey_in=survey_in,
            files=files,
        )
        return SurveyRead.model_validate(obj=survey_db)
    except SurveyCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.post(
    path="/surveys/{survey_id}/tree_photos",
    response_model=list[PhotoRead],
    status_code=status.HTTP_201_CREATED,
    summary="Добавление фотографий растения",
    description="Загружает одну или несколько фотографий общего вида\
        растения и привязывает их к существующему обследованию.",
)
async def add_tree_photos_to_survey(
    survey_id: int,
    files: list[UploadFile],
    service: PhotoService = Depends(),
) -> list[PhotoRead]:
    try:
        tree_photos = await service.upload_and_link_photos(
            files=files,
            survey_id=survey_id,
        )
        return [PhotoRead.model_validate(photo) for photo in tree_photos]
    except PhotoCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ExceptionDetails.FAILED_CREATE_PHOTO} {e}",
        )


@router.patch(
    path="/surveys/{survey_id}",
    response_model=SurveyRead,
    summary="Изменение обследования",
    description="Изменяет поля записи обследования по идентификатору (id).",
)
async def update_survey(
    survey_id: int,
    survey_in: SurveyUpdate,
    service: SurveyService = Depends(),
) -> SurveyRead:
    try:
        survey_update_db = await service.update_survey(
            obj_id=survey_id, obj_in=survey_in
        )
        return SurveyRead.model_validate(obj=survey_update_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except SurveyUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete(
    path="/surveys/{survey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление конкретного обследования",
    description="Удаляет обследование по идентификатору (id).",
)
async def delete_survey(
    survey_id: int, service: SurveyService = Depends()
) -> None:
    try:
        await service.delete_with_photos(survey_id=survey_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except SurveyRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
