from fastapi import Depends

from app.core.exceptions import (
    ExceptionDetails,
    NotFoundError,
    RoleCreationError,
    RoleRemovingError,
    RoleUpdatingError,
)
from app.models import Role
from app.repositories.role import RoleRepository
from app.schemas import RoleCreate, RoleUpdate
from app.services.mixins import CreateObjMixin, DeleteObjMixin, UpdateObjMixin


class RoleService(CreateObjMixin, UpdateObjMixin, DeleteObjMixin):
    def __init__(
        self,
        repo: RoleRepository = Depends(),
    ) -> None:
        self.repo = repo

    async def get_all_roles(self) -> list[Role]:
        roles_db = await self.repo.get_multi()
        return roles_db

    async def get_role(self, obj_id: int) -> Role:
        role_db = await self.repo.get(id=obj_id)
        if not role_db:
            raise NotFoundError(
                ExceptionDetails.get_not_found_detail(
                    model_name=self.repo.model.verbose_name(),
                    id=obj_id,
                )
            )
        return role_db

    async def create_role(self, obj_in: RoleCreate) -> Role:
        try:
            role = await self.create_obj(obj_in=obj_in)
            return role
        except Exception as e:
            raise RoleCreationError(
                f"{ExceptionDetails.FAILED_CREATE_RECORD}: {e}"
            ) from e

    async def update_role(self, obj_id: int, obj_in: RoleUpdate) -> Role:
        try:
            role_db = await self.repo.get(id=obj_id)
            if not role_db:
                raise NotFoundError(
                    ExceptionDetails.get_not_found_detail(
                        model_name=self.repo.model.verbose_name(),
                        id=obj_id,
                    )
                )
            role = await self.update_obj(db_obj=role_db, obj_in=obj_in)
            return role
        except NotFoundError:
            raise
        except Exception as e:
            raise RoleUpdatingError(
                f"{ExceptionDetails.FAILED_UPDATE_RECORD}: {e}"
            ) from e

    async def delete_role(self, role_id: int) -> None:
        try:
            await self.delete_obj(obj_id=role_id)
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise RoleRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
