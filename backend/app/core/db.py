from app.core.config import settings
from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    declared_attr,
    mapped_column,
)


class PreBase:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(url=settings.database_url)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
