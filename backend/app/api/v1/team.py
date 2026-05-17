from fastapi import Depends, status
from fastapi.routing import APIRouter

from app.api.v1.dependencies import get_team_db
from app.core.permissions import IsAdmin, permission_dependency
from app.models import Team
from app.schemas import TeamCreate, TeamRead, TeamUpdate
from app.services.team_service import TeamService

router = APIRouter()


@router.get(
    path="/",
    response_model=list[TeamRead],
    summary="Получение списка команд волонтеров",
    description="Показывает список всех зарегистрированных команд.",
)
async def get_all_teams(service: TeamService = Depends()) -> list[TeamRead]:
    teams_db = await service.get_all_teams()
    return [TeamRead.model_validate(obj=team_db) for team_db in teams_db]


@router.get(
    path="/{team_id}",
    response_model=TeamRead,
    summary="Получение команды волонтеров",
    description="Показывает команду по ее идентификатору (id).",
)
async def get_team(
    team_db: Team = Depends(dependency=get_team_db),
) -> TeamRead:
    return TeamRead.model_validate(obj=team_db)


@router.post(
    path="/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой команды волонтеров",
    description="Создает новую команду в системе.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def create_team(
    team_in: TeamCreate,
    service: TeamService = Depends(),
) -> TeamRead:
    team_db = await service.create_team(team_in=team_in)
    return TeamRead.model_validate(obj=team_db)


@router.patch(
    path="/{team_id}",
    response_model=TeamRead,
    summary="Изменение команды волонтеров",
    description="Изменяет поля записи в команде \
        по ее идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def update_team(
    team_in: TeamUpdate,
    team_db: Team = Depends(dependency=get_team_db),
    service: TeamService = Depends(),
) -> TeamRead:
    team_update_db = await service.update_team(
        team_db=team_db, team_in=team_in
    )
    return TeamRead.model_validate(obj=team_update_db)


@router.delete(
    path="/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление команды волонтеров",
    description="Удаляет команду по ее идентификатору (id)./n\
        Невозможно удалить команду, к которой прикреплены волонтеры",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def delete_team(
    team_db: Team = Depends(dependency=get_team_db),
    service: TeamService = Depends(),
) -> None:
    await service.delete_team(team=team_db)
