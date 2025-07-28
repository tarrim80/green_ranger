from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.exceptions import (
    NotFoundError,
    RoleRemovingError,
    RoleUpdatingError,
)
from app.core.permissions import IsAdmin, permission_dependency
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
    service: RoleService = Depends(),
) -> list[RoleRead]:
    roles_db = await service.get_all_roles()
    return [RoleRead.model_validate(obj=role_db) for role_db in roles_db]


@router.get(
    path="/{role_id}",
    response_model=RoleRead,
    summary="Получение роли",
    description="Показывает роль по ее идентификатору (id).",
)
async def get_role(role_id: int, service: RoleService = Depends()) -> RoleRead:
    try:
        role_db = await service.get_role(obj_id=role_id)
        return RoleRead.model_validate(obj=role_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e


@router.post(
    path="/",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой роли",
    description="Создает новую уникальную роль в системе. \
        Используется для разграничения прав доступа пользователей.",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def create_role(
    role_in: RoleCreate,
    service: RoleService = Depends(),
) -> RoleRead:
    role_db = await service.create_role(obj_in=role_in)
    return RoleRead.model_validate(obj=role_db)


@router.patch(
    path="/{role_id}",
    response_model=RoleRead,
    summary="Изменение роли",
    description="Изменяет поля записи в конкретной роли \
        по ее идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    service: RoleService = Depends(),
) -> RoleRead:
    try:
        role_update_db = await service.update_role(
            obj_id=role_id, obj_in=role_in
        )
        return RoleRead.model_validate(obj=role_update_db)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from e
    except RoleUpdatingError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete(
    path="/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли",
    description="Удаляет роль по ее идентификатору (id).",
    dependencies=[
        Depends(dependency=permission_dependency(permission=IsAdmin))
    ],
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
