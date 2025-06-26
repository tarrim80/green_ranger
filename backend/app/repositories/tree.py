from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models import Tree
from app.repositories.base import BaseRepository
from app.schemas import TreeCreate, TreeUpdate


class TreeRepository(BaseRepository[Tree, TreeCreate, TreeUpdate]):
    model = Tree

    def __init__(
        self,
        session: Annotated[
            AsyncSession, Depends(dependency=get_async_session)
        ],
    ) -> None:
        super().__init__(session=session)
