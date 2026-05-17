from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    status,
)

from app.api.v1.dependencies import (
    check_survey_creation_access,
    check_survey_modification_access,
    get_survey_db,
    get_tree_from_form,
    resolve_survey_status,
)
from app.core.permissions import (
    IsCurator,
    IsVolunteer,
    permission_dependency,
)
from app.core.user import current_user
from app.models import Survey, User
from app.models.tree import Tree
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
    survey_db: Survey = Depends(dependency=get_survey_db),
) -> SurveyRead:
    return SurveyRead.model_validate(obj=survey_db)


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
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_survey_creation_access),
    ],
)
async def create_survey(
    tree_db: Tree = Depends(dependency=get_tree_from_form),
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
        tree_id=tree_db.id,
        age=age,
        height=height,
        diameter=diameter,
        trunk_count=trunk_count,
        condition=condition,
        is_emergency_report=is_emergency_report,
        note=note,
        author_id=current_user.id,
    )
    survey_db = await service.create_with_photos(
        survey_in=survey_in,
        files=files,
    )
    return SurveyRead.model_validate(obj=survey_db)


@router.patch(
    path="/surveys/{survey_id}",
    response_model=SurveyRead,
    summary="Изменение обследования",
    description="Изменяет поля записи обследования по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsVolunteer)),
        Depends(dependency=check_survey_modification_access),
    ],
)
async def update_survey(
    survey_db: Survey = Depends(dependency=get_survey_db),
    age: int | None = Form(default=None),
    height: float | None = Form(default=None),
    diameter: float | None = Form(default=None),
    trunk_count: int | None = Form(default=None),
    condition: TreeConditionEnum | None = Form(default=None),
    is_emergency_report: bool | None = Form(default=None),
    note: str | None = Form(default=None),
    files: list[UploadFile] | None = File(default=None),
    survey_status: SurveyStatusEnum = Depends(
        dependency=resolve_survey_status
    ),
    service: SurveyService = Depends(),
) -> SurveyRead:
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
        survey_db=survey_db,
        obj_in=survey_update_in,
        files=files,
    )
    return SurveyRead.model_validate(obj=survey_update_db)


@router.delete(
    path="/surveys/{survey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление конкретного обследования",
    description="Удаляет обследование по идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsCurator)),
        Depends(dependency=check_survey_modification_access),
    ],
)
# TODO Запретить удалять обследования. Можно Только архивировать!
async def delete_survey(
    survey_db: Survey = Depends(dependency=get_survey_db),
    service: SurveyService = Depends(),
) -> None:
    await service.delete_with_photos(survey_db=survey_db)
