from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.config import settings

engine = create_async_engine(url=settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Провайдер асинхронной сессии для зависимостей FastAPI."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
