from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

from app.schemas import RoleRead


class UserRead(schemas.BaseUser[int]):
    telegram_id: int
    firstname: str | None = None
    lastname: str | None = None
    roles: list[RoleRead]


class UserCreate(schemas.BaseUserCreate):
    telegram_id: int
    firstname: str | None = None
    lastname: str | None = None
    role_ids: list[int]


class UserUpdate(schemas.BaseUserUpdate):
    firstname: str | None = None
    lastname: str | None = None
    role_ids: list[int] | None = None


class UserShortRead(BaseModel):
    id: int
    fullname: str

    model_config = ConfigDict(from_attributes=True)
