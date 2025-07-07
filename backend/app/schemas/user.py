from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

from app.schemas import RoleRead


class UserRead(schemas.BaseUser[int]):
    telegram_id: int
    firstname: str | None
    lastname: str | None
    roles: list[RoleRead]
    team_id: int | None


class UserCreate(schemas.BaseUserCreate):
    telegram_id: int
    firstname: str | None = None
    lastname: str | None = None
    role_ids: list[int]
    team_id: int | None = None


class UserUpdate(schemas.BaseUserUpdate):
    firstname: str | None = None
    lastname: str | None = None
    role_ids: list[int] | None = None
    team_id: int | None = None


class UserShortRead(BaseModel):
    id: int
    fullname: str

    model_config = ConfigDict(from_attributes=True)
