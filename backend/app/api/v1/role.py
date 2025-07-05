from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails
from app.core.exceptions import NotFoundError, RoleRemovingError
from app.repositories import RoleRepository
from app.schemas import RoleCreate, RoleRead, RoleUpdate
from app.services.role_service import RoleService

router = APIRouter()


@router.get(
    path="/",
    response_model=list[RoleRead],
    summary="Получение списка ролей",
    description="Показывает список всех возможных ролей пользователя.",
)
async def get_all_roles(
    repo: RoleRepository = Depends(),
) -> list[RoleRead]:
    roles_db = await repo.get_multi()
    return [RoleRead.model_validate(obj=role_db) for role_db in roles_db]


@router.get(
    path="/{role_id}",
    response_model=RoleRead,
    summary="Получение роли",
    description="Показывает роль по ее идентификатору (id).",
)
async def get_role(role_id: int, repo: RoleRepository = Depends()) -> RoleRead:
    role_db = await repo.get(id=role_id)
    if not role_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Роль", id=role_id
            ),
        )
    return RoleRead.model_validate(obj=role_db)


@router.post(
    path="/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    description="Создает новую уникальную роль в системе. \
        Используется для разграничения прав доступа пользователей.",
)
async def create_role(
    role_in: RoleCreate, repo: RoleRepository = Depends()
) -> RoleRead:
    role_db = await repo.create(obj_in=role_in)
    return RoleRead.model_validate(obj=role_db)


@router.patch(
    path="/{role_id}",
    response_model=RoleRead,
    summary="Изменение роли",
    description="Изменяет поля записи в конкретной роли \
        по ее идентификатору (id).",
)
async def update_role(
    role_id: int, role_in: RoleUpdate, repo: RoleRepository = Depends()
) -> RoleRead:
    role_db = await repo.get(id=role_id)
    if not role_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(
                model_name="Роль", id=role_id
            ),
        )
    role_update_db = await repo.update(db_obj=role_db, obj_in=role_in)
    return RoleRead.model_validate(obj=role_update_db)


@router.delete(
    path="/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли",
    description="Удаляет роль по ее идентификатору (id).",
)
async def delete_role(role_id: int, service: RoleService = Depends()) -> None:
    try:
        await service.delete_role(role_id=role_id)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except RoleRemovingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
