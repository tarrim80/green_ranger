from fastapi import Depends

from app.core.constants import ExceptionDetails
from app.core.exceptions import NotFoundError, RoleRemovingError
from app.core.transaction_manager import atomic_transaction
from app.repositories.role import RoleRepository


class RoleService:
    def __init__(
        self,
        repo: RoleRepository = Depends(),
    ) -> None:
        self.repo = repo

    async def delete_role(self, role_id: int) -> None:
        try:
            async with atomic_transaction(session=self.repo.session):
                role = await self.repo.remove(id=role_id)
                if not role:
                    raise NotFoundError(
                        ExceptionDetails.get_not_found_detail(
                            model_name="Роль", id=role_id
                        )
                    )
        except NotFoundError as e:
            raise
        except Exception as e:
            raise RoleRemovingError(
                f"{ExceptionDetails.FAILED_REMOVE_RECORD}: {e}"
            ) from e
