from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict

from app.schemas.enums import RoleEnum

# TODO: USER_FIELDS_CONFIG


class UserRead(schemas.BaseUser[int]):
    telegram_id: int
    firstname: str | None
    lastname: str | None
    role: RoleEnum
    team_id: int | None


class UserCreate(schemas.BaseUserCreate):
    telegram_id: int
    firstname: str | None = None
    lastname: str | None = None
    team_id: int | None = None


class UserUpdate(schemas.BaseUserUpdate):
    firstname: str | None = None
    lastname: str | None = None
    role: RoleEnum | None = None
    team_id: int | None = None


class UserShortRead(BaseModel):
    id: int
    fullname: str

    model_config = ConfigDict(from_attributes=True)
