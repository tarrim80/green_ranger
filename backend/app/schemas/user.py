from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    telegram_id: int
    name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    telegram_id: int
    name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    name: Optional[str] = None
