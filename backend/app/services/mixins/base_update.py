from typing import Generic, TypeVar

from pydantic import BaseModel

from app.core.transaction_manager import atomic_transaction
from app.repositories.base import BaseRepository

TRepository = TypeVar("TRepository", bound=BaseRepository)
TModel = TypeVar("TModel")
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class UpdateObjMixin(Generic[TRepository, TModel, TUpdate]):
    """Миксин для обновления объекта в базе данных."""

    repo: TRepository

    async def update_obj(self, db_obj: TModel, obj_in: TUpdate) -> TModel:
        """Выполняет обновление объекта в рамках транзакции."""
        try:
            async with atomic_transaction(session=self.repo.session):
                obj = await self.repo.update(db_obj=db_obj, obj_in=obj_in)
            return obj
        except Exception:
            raise
