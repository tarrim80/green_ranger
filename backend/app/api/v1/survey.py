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
    NotFoundError,
    PermissionDenniedError,
    SurveyCreationError,
    SurveyRemovingError,
    SurveyUpdatingError,
)
from app.core.permissions import IsCurator, IsVolunteer, permission_dependency
from app.core.user import current_user
from app.models import User
from app.schemas import (
    SurveyCreate,
    SurveyRead,
    SurveyStatusEnum,
    SurveyUpdate,
    TreeConditionEnum,
)
from app.schemas.defaults import SurveyDefaults
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
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
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
    current_user: "User" = Depends(dependency=current_user),
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
            user=current_user,
        )
        return SurveyRead.model_validate(obj=survey_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except PermissionDenniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e
    except SurveyCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.patch(
    path="/surveys/{survey_id}",
    response_model=SurveyRead,
    summary="Изменение обследования",
    description="Изменяет поля записи обследования по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer))
    ],
)
async def update_survey(
    survey_id: int,
    age: int | None = Form(default=None),
    height: float | None = Form(default=None),
    diameter: float | None = Form(default=None),
    trunk_count: int | None = Form(default=None),
    condition: TreeConditionEnum | None = Form(default=None),
    is_emergency_report: bool | None = Form(default=None),
    note: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
    survey_status: SurveyStatusEnum | None = Form(default=None),
    current_user: User = Depends(dependency=current_user),
    service: SurveyService = Depends(),
) -> SurveyRead:
    try:
        survey_update_in = SurveyUpdate(
            age=age,
            height=height,
            diameter=diameter,
            trunk_count=trunk_count,
            condition=condition,
            is_emergency_report=is_emergency_report,
            note=note,
            survey_status=survey_status,
        )
        survey_update_db = await service.update_survey_with_photos(
            obj_id=survey_id,
            obj_in=survey_update_in,
            user=current_user,
            files=files,
        )
        return SurveyRead.model_validate(obj=survey_update_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except PermissionDenniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
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
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator))
    ],
)
async def delete_survey(
    survey_id: int,
    service: SurveyService = Depends(),
    user: User = Depends(current_user),
) -> None:
    try:
        await service.delete_with_photos(survey_id=survey_id, user=user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except PermissionDenniedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from e
    except SurveyRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
