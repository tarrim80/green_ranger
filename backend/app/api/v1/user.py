from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ExceptionDetails
from app.core.db import get_async_session
from app.core.user import auth_backend, fastapi_users
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserShortRead, UserUpdate

router = APIRouter()

router.include_router(
    router=fastapi_users.get_auth_router(backend=auth_backend),
    prefix="/auth/jwt",
    tags=["Авторизация"],
)
router.include_router(
    router=fastapi_users.get_register_router(
        user_schema=UserRead, user_create_schema=UserCreate
    ),
    prefix="/auth",
    tags=["Авторизация"],
)
router.include_router(
    router=fastapi_users.get_users_router(
        user_schema=UserRead, user_update_schema=UserUpdate
    ),
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
    "/users",
    response_model=list[UserShortRead],
    tags=["Пользователи"],
    description="Список пользователей в кратком виде.",
)
async def list_users(
    session: AsyncSession = Depends(get_async_session),
) -> list[UserShortRead]:
    result = await session.execute(select(User))
    users_db = result.scalars().all()
    return [UserShortRead.model_validate(obj=user_db) for user_db in users_db]


@router.delete(
    "/users/{id}",
    tags=["Пользователи"],
    deprecated=True,
    description="Не используйте удаление, деактивируйте пользователей.",
)
def delete_user(id: int):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ExceptionDetails.NOT_ALLOWED_REMOVE_USERS,
    )
