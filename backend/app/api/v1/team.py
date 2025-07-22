from fastapi import Body, Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.exceptions import (
    NotAllowedError,
    NotFoundError,
    TeamCreationError,
    TeamRemovingError,
    TeamUpdatingError,
)
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
async def get_team(team_id: int, service: TeamService = Depends()) -> TeamRead:
    try:
        team_db = await service.get_team(obj_id=team_id)
        return TeamRead.model_validate(obj=team_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.post(
    path="/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой команды волонтеров",
    description="Создает новую команду в системе.",
)
async def create_team(
    team_in: TeamCreate,
    service: TeamService = Depends(),
) -> TeamRead:
    try:
        team_db = await service.create_team(team_in=team_in)
        return TeamRead.model_validate(obj=team_db)
    except TeamCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    path="/{team_id}",
    response_model=TeamRead,
    summary="Изменение команды волонтеров",
    description="Изменяет поля записи в команде \
        по ее идентификатору (id).",
)
async def update_team(
    team_id: int, team_in: TeamUpdate, service: TeamService = Depends()
) -> TeamRead:
    try:
        team_update_db = await service.update_team(
            team_id=team_id, team_in=team_in
        )
        return TeamRead.model_validate(obj=team_update_db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        ) from e
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except TeamUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post(
    path="/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=TeamRead,
    summary="Добаление в команду волонтеров",
    description="Добавляет в команду с идентификатором (id) одного \
        или нескольких волонтеровю",
)
async def add_members_to_team(
    team_id: int,
    member_ids: list[int] = Body(..., embed=True),
    service: TeamService = Depends(),
) -> TeamRead:
    try:
        team_db = await service.add_members(
            team_id=team_id, member_ids=member_ids
        )
        return TeamRead.model_validate(team_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except NotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except TeamCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete(
    path="/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=TeamRead,
    summary="Исключение волонтеров из команды",
    description="Исключает из команды с идентификатором (id) одного \
        или нескольких волонтеров.",
)
async def remove_members_from_team(
    team_id: int,
    member_ids: list[int] = Body(..., embed=True),
    service: TeamService = Depends(),
) -> TeamRead:
    try:
        team_db = await service.remove_members(
            team_id=team_id, member_ids=member_ids
        )
        return TeamRead.model_validate(team_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except NotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from e
    except TeamRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete(
    path="/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление команды волонтеров",
    description="Удаляет команду по ее идентификатору (id)./n\
        Невозможно удалить команду, к которой прикреплены волонтеры",
)
async def delete_team(team_id: int, service: TeamService = Depends()) -> None:
    try:
        await service.delete_team(team_id=team_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except NotAllowedError as e:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=str(e),
        ) from e
    except TeamRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
