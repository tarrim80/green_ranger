from typing import Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DEFAULT_LIMIT

TModel = TypeVar("TModel")
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class BaseRepository(Generic[TModel, TCreate, TUpdate]):
    model: Type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int) -> TModel | None:
        result = await self.session.execute(
            statement=select(self.model).where(self.model.id == id)  # type: ignore
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, skip: int = 0, limit: int = DEFAULT_LIMIT
    ) -> Sequence[TModel]:
        result = await self.session.execute(
            statement=select(self.model).offset(offset=skip).limit(limit=limit)
        )
        return result.scalars().all()

    async def get_by_ids(self, ids: list[int]) -> list[TModel]:
        """Получает объекты по списку их ID."""
        if not ids:
            return []
        result = await self.session.execute(
            statement=select(self.model).where(self.model.id.in_(ids))  # type: ignore
        )
        return list(result.scalars().all())

    async def create(self, obj_in: TCreate) -> TModel:
        obj = self.model(**obj_in.model_dump())
        self.session.add(instance=obj)
        return obj

    async def create_many(self, objs_in: list[TCreate]) -> list[TModel]:
        db_objs = [self.model(**obj_in.model_dump()) for obj_in in objs_in]

        self.session.add_all(instances=db_objs)
        return db_objs

    async def update(self, db_obj: TModel, obj_in: TUpdate) -> TModel:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self.session.add(instance=db_obj)
        return db_obj

    async def remove(self, id: int) -> TModel | None:
        obj = await self.get(id=id)
        if not obj:
            return None
        await self.session.delete(instance=obj)
        return obj
