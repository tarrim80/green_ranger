from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def atomic_transaction(session: AsyncSession) -> AsyncIterator[None]:
    try:
        yield
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise e
