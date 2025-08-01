from typing import Generic, TypeVar

from pydantic import BaseModel

from app.core.transaction_manager import atomic_transaction
from app.repositories.base import BaseRepository

TRepository = TypeVar("TRepository", bound=BaseRepository)
TModel = TypeVar("TModel")
TCreate = TypeVar("TCreate", bound=BaseModel)


class CreateObjMixin(Generic[TRepository, TModel, TCreate]):
    """Миксин для создания объекта в базе данных."""

    repo: TRepository

    async def create_obj(self, obj_in: TCreate) -> TModel:
        """Выполняет создание объекта в рамках транзакции."""
        try:
            async with atomic_transaction(session=self.repo.session):
                obj = await self.repo.create(obj_in=obj_in)
            return obj
        except Exception:
            raise
