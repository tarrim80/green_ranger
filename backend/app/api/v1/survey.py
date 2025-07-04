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
from app.core.exceptions import PhotoCreationError, SurveyCreationError
from app.core.user import current_user
from app.models import User
from app.schemas import PhotoRead, SurveyCreate, SurveyRead, TreeConditionEnum
from app.services.photo_service import PhotoService
from app.services.survey_service import SurveyService

router = APIRouter()


@router.post(
    path="/",
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
    path="/{survey_id}/tree_photos",
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
