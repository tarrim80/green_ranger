from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from app.core.constants import ExceptionDetails
from app.repositories import RoleRepository
from app.schemas import RoleCreate, RoleRead, RoleUpdate

router = APIRouter()


@router.get(path="/", response_model=list[RoleRead])
async def get_all_roles(
    repo: RoleRepository = Depends(),
) -> list[RoleRead]:
    db_roles = await repo.get_multi()
    return [RoleRead.model_validate(obj=role) for role in db_roles]


@router.get(path="/{role_id}", response_model=RoleRead)
async def get_role(role_id: int, repo: RoleRepository = Depends()) -> RoleRead:
    role_db = await repo.get(id=role_id)
    if not role_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Роль"),
        )
    return RoleRead.model_validate(obj=role_db)


@router.post(
    path="/", response_model=RoleRead, status_code=status.HTTP_201_CREATED
)
async def create_role(
    role_in: RoleCreate, repo: RoleRepository = Depends()
) -> RoleRead:
    role_db = await repo.create(obj_in=role_in)
    return RoleRead.model_validate(obj=role_db)


@router.patch(path="/{role_id}", response_model=RoleRead)
async def role_update(
    role_id: int, role_in: RoleUpdate, repo: RoleRepository = Depends()
) -> RoleRead:
    role_db = await repo.get(id=role_id)
    if not role_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Роль"),
        )
    role_update_db = await repo.update(db_obj=role_db, obj_in=role_in)
    return RoleRead.model_validate(obj=role_update_db)


@router.delete(path="/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def role_delete(role_id: int, repo: RoleRepository = Depends()):
    if not await repo.remove(id=role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ExceptionDetails.get_not_found_detail(model_name="Роль"),
        )
