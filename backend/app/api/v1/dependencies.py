from fastapi import Depends, Form

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    PermissionDenniedError,
)
from app.core.permissions import (
    IsAdmin,
    IsSectorCurator,
    IsSectorCuratorOrCorrectTeam,
    IsSurveyDefectOwnerOrCurator,
    IsSurveyOwnerOrCurator,
    IsTreeCuratorOrCorrectTeam,
)
from app.core.user import current_user
from app.models import Sector, Survey, SurveyDefect, Team, Tree, User
from app.models.photo import Photo
from app.repositories import (
    PhotoRepository,
    SectorRepository,
    SurveyDefectRepository,
    SurveyRepository,
    TeamRepository,
    TreeRepository,
)
from app.schemas import RoleEnum, SurveyStatusEnum, TreeCreate


async def get_tree_db(
    tree_id: int,
    tree_repo: TreeRepository = Depends(),
) -> Tree:
    """Получает растение по его идентификатору."""

    tree_db = await tree_repo.get(id=tree_id)
    if not tree_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=TreeRepository.model.verbose_name(),
                id=tree_id,
            )
        )
    return tree_db


async def get_tree_from_form(
    tree_id: int = Form(default=...),
    tree_repo: TreeRepository = Depends(),
) -> Tree:
    """
    Извлекает ID растения из формы возвращает объект Tree.
    Используется как промежуточная зависимость для проверки прав доступа к
    растению.
    """
    return await get_tree_db(tree_id=tree_id, tree_repo=tree_repo)


async def get_sector_db(
    sector_id: int,
    sector_repo: SectorRepository = Depends(),
) -> Sector:
    """Получает участок по его идентификатору."""

    sector_db = await sector_repo.get(id=sector_id)
    if not sector_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=SectorRepository.model.verbose_name(),
                id=sector_id,
            )
        )
    return sector_db


async def get_sector_from_body(
    tree_in: TreeCreate,
    repo: SectorRepository = Depends(),
) -> Sector:
    """
    Извлекает ID участка из данных растения и возвращает объект Sector.
    Используется как промежуточная зависимость для проверки прав доступа к
    участку.
    """

    return await get_sector_db(sector_id=tree_in.sector_id, sector_repo=repo)


async def get_team_db(
    team_id: int, team_repo: TeamRepository = Depends()
) -> Team:
    """Получает команду по её идентификатору."""
    team_db = await team_repo.get(id=team_id)
    if not team_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=team_repo.model.verbose_name(),
                id=team_id,
            )
        )
    return team_db


async def get_survey_db(
    survey_id: int, survey_repo: SurveyRepository = Depends()
) -> Survey:
    """Получает обследование по его идентификатору."""
    survey_db = await survey_repo.get(id=survey_id)
    if not survey_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=survey_repo.model.verbose_name(),
                id=survey_id,
            )
        )
    return survey_db


async def get_survey_defect_db(
    defect_id: int, defect_repo: SurveyDefectRepository = Depends()
) -> SurveyDefect:
    """Получает конкретный дефект по его идентификатору."""
    defect_db = await defect_repo.get(id=defect_id)
    if not defect_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=defect_repo.model.verbose_name(),
                id=defect_id,
            )
        )

    return defect_db


async def get_photo_db(
    photo_id: int,
    photo_repo: PhotoRepository = Depends(),
) -> Photo:
    photo_db = await photo_repo.get(id=photo_id)
    if not photo_db:
        raise NotFoundError(
            ExceptionDetails.get_not_found_detail(
                model_name=photo_repo.model.verbose_name(),
                id=photo_id,
            )
        )

    return photo_db


async def check_tree_creation_access(
    sector: Sector = Depends(dependency=get_sector_from_body),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к созданию растения на указанном участке."""

    permission = await IsSectorCuratorOrCorrectTeam().has_obj_permission(
        user=user, obj=sector
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_tree_modification_access(
    tree: Tree = Depends(dependency=get_tree_db),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к редактированию или удалению растения."""

    permission = await IsTreeCuratorOrCorrectTeam().has_obj_permission(
        user=user, obj=tree
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_survey_creation_access(
    tree: Tree = Depends(dependency=get_tree_from_form),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к созданию обследования указанного растения."""

    permission = await IsTreeCuratorOrCorrectTeam().has_obj_permission(
        user=user, obj=tree
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_survey_modification_access(
    survey: Survey = Depends(dependency=get_survey_db),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к редактированию или удалению обследования."""

    permission = await IsSurveyOwnerOrCurator().has_obj_permission(
        user=user, obj=survey
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_survey_defect_modification_access(
    defect: SurveyDefect = Depends(dependency=get_survey_defect_db),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к редактированию или удалению кокретного дефекта."""

    permission = await IsSurveyDefectOwnerOrCurator().has_obj_permission(
        user=user, obj=defect
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_sector_modification_access(
    sector: Sector = Depends(dependency=get_sector_db),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к редактированию или удалению участка."""
    permission = await IsSectorCurator().has_obj_permission(
        user=user, obj=sector
    )
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def check_photo_uploading_access(
    defect_type_id: int | None = None,
    survey_id: int | None = None,
    survey_defect_id: int | None = None,
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к загрузке фотографии."""

    if defect_type_id:
        permission = await IsAdmin().has_permission(user=user)
        if not permission:
            raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)

    if survey_id:
        survey = await get_survey_db(survey_id=survey_id)
        await check_survey_modification_access(survey=survey)

    if survey_defect_id:
        survey_defect = await get_survey_defect_db(defect_id=survey_defect_id)
        await check_survey_defect_modification_access(defect=survey_defect)


async def check_photo_deletion_access(
    photo_db: Photo = Depends(dependency=get_photo_db),
    user: User = Depends(dependency=current_user),
) -> None:
    """Проверяет доступ к удалению фотографии."""
    if photo_db.defect_type_id:
        permission = await IsAdmin().has_permission(user=user)
    elif photo_db.tree_photo:
        permission = await IsSurveyOwnerOrCurator().has_obj_permission(
            user=user, obj=photo_db.tree_photo
        )
    elif photo_db.survey_defect_photo:
        permission = await IsSurveyDefectOwnerOrCurator().has_obj_permission(
            user=user, obj=photo_db.survey_defect_photo
        )
    else:
        permission = await IsAdmin().has_permission(user=user)
    if not permission:
        raise PermissionDenniedError(ExceptionDetails.NO_RIGHT_FOR_ACTION)


async def resolve_survey_status(
    survey_status: SurveyStatusEnum | None = Form(default=None),
    user: User = Depends(dependency=current_user),
) -> SurveyStatusEnum:
    if user.role == RoleEnum.VOLUNTEER:
        return SurveyStatusEnum.ON_REVIEW
    return survey_status or SurveyStatusEnum.ON_REVIEW
