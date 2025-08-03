from typing import Annotated

from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import RoleEnum

USER_FIELDS_CONFIG = {
    "id": Field(description="Уникальный идентификатор", examples=[1, 2, 3]),
    "telegram_id": Field(
        description="Уникальный идентификатор в телеграмм",
        examples=[1, 2, 3],
    ),
    "firstname": Field(
        description="Имя пользователя", examples=["Иван"], max_length=100
    ),
    "lastname": Field(
        description="Фамилия пользователя", examples=["Иванов"], max_length=100
    ),
    "fullname": Field(description="Полное имя", examples=["Иван Иванов"]),
    "role": Field(description="Роль пользователя. Регулирует права доступа"),
    "team_id": Field(
        description="Идентификатор команды волонтёров", examples=[1, 2, 3]
    ),
    "is_active": Field(
        description="Признак активности пользователя", examples=[True, False]
    ),
}


class UserRead(schemas.BaseUser[int]):
    """Схема для чтения данных пользователя."""

    telegram_id: Annotated[int, USER_FIELDS_CONFIG["telegram_id"]]
    firstname: Annotated[str | None, USER_FIELDS_CONFIG["firstname"]]
    lastname: Annotated[str | None, USER_FIELDS_CONFIG["lastname"]]
    role: Annotated[RoleEnum, USER_FIELDS_CONFIG["role"]]
    team_id: Annotated[int | None, USER_FIELDS_CONFIG["team_id"]]


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания пользователя."""

    telegram_id: Annotated[int, USER_FIELDS_CONFIG["telegram_id"]]
    firstname: Annotated[str | None, USER_FIELDS_CONFIG["firstname"]] = None
    lastname: Annotated[str | None, USER_FIELDS_CONFIG["lastname"]] = None
    team_id: Annotated[int | None, USER_FIELDS_CONFIG["team_id"]] = None


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления данных пользователя."""

    firstname: Annotated[str | None, USER_FIELDS_CONFIG["firstname"]] = None
    lastname: Annotated[str | None, USER_FIELDS_CONFIG["lastname"]] = None
    role: Annotated[RoleEnum | None, USER_FIELDS_CONFIG["role"]] = None
    team_id: Annotated[int | None, USER_FIELDS_CONFIG["team_id"]] = None


class UserShortRead(BaseModel):
    """Схема для краткого представления пользователя."""

    id: Annotated[int, USER_FIELDS_CONFIG["id"]]
    fullname: Annotated[str, USER_FIELDS_CONFIG["fullname"]]
    role: Annotated[RoleEnum, USER_FIELDS_CONFIG["role"]]
    is_active: Annotated[bool, USER_FIELDS_CONFIG["is_active"]]

    model_config = ConfigDict(from_attributes=True)
