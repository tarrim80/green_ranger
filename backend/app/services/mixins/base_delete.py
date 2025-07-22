from typing import Generic, TypeVar

from app.core.exceptions import ExceptionDetails, NotFoundError
from app.core.transaction_manager import atomic_transaction
from app.repositories.base import BaseRepository

TRepository = TypeVar("TRepository", bound=BaseRepository)
TModel = TypeVar("TModel")


class DeleteObjMixin(Generic[TRepository, TModel]):

    repo: TRepository

    async def delete_obj(self, obj_id: int) -> TModel:
        try:
            async with atomic_transaction(session=self.repo.session):
                obj = await self.repo.remove(id=obj_id)
                if not obj:
                    raise NotFoundError(
                        ExceptionDetails.get_not_found_detail(
                            model_name=self.repo.model.verbose_name(),
                            id=obj_id,
                        )
                    )
            return obj
        except NotFoundError:
            raise
        except Exception:
            raise
