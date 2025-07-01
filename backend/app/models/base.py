from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings
from app.services.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    """
    Базовая абстракная модель.
    Обеспечивает формирование составных имен. Формирует имя таблицы.
    """

    __abstract__ = True

    metadata = MetaData(
        naming_convention=settings.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}"
