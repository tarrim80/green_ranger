from typing import Protocol

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.config import settings
from app.utils.case_converter import camel_case_to_snake_case


class VerboseModel(Protocol):
    @classmethod
    def verbose_name(cls) -> str: ...
    @classmethod
    def verbose_name_plural(cls) -> str: ...


class Base(DeclarativeBase):
    """
    Базовая абстракная модель.
    Обеспечивает формирование составных имен. Формирует имя таблицы.
    Формирует альтернативные имена.
    """

    __abstract__ = True

    __verbose_name__ = None
    __verbose_name_plural__ = None

    metadata = MetaData(
        naming_convention=settings.naming_convention,
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(input_str=cls.__name__)}"

    @classmethod
    def verbose_name(cls) -> str:
        return cls.__verbose_name__ or cls.__name__

    @classmethod
    def verbose_name_plural(cls) -> str:
        return cls.__verbose_name_plural__ or cls.__name__ + "s"
