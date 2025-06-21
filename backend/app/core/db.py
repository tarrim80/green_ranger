from typing import AsyncGenerator

from app.core.config import settings
from app.serviсes.case_converter import camel_case_to_snake_case
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import declarative_base, declared_attr


class PreBase:
    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}"  # type: ignore


Base = declarative_base(cls=PreBase)

engine = create_async_engine(url=settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as async_session:
        yield async_session
