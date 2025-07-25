import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, create_refresh_token
from app.core.config import settings
from app.core.constants import TOKEN_TYPE
from app.core.db import get_async_session
from app.core.exceptions import ExceptionDetails
from app.core.user import (
    UserManager,
    auth_backend,
    fastapi_users,
    get_user_manager,
)
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserShortRead, UserUpdate

bearer_scheme = HTTPBearer()

auth_router = APIRouter()

user_router = APIRouter(
    dependencies=[Depends(bearer_scheme)],
)

auth_router.include_router(
    router=fastapi_users.get_auth_router(backend=auth_backend),
)

auth_router.include_router(
    router=fastapi_users.get_register_router(
        user_schema=UserRead, user_create_schema=UserCreate
    ),
    prefix="/jwt",
)
user_router.include_router(
    router=fastapi_users.get_users_router(
        user_schema=UserRead, user_update_schema=UserUpdate
    ),
)


@auth_router.post("/jwt/login")
async def auth_login(
    user_manager: UserManager = Depends(get_user_manager),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> JSONResponse:
    user = await user_manager.authenticate(credentials=form_data)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_type = TOKEN_TYPE
    access_token = await create_access_token(user=user)
    refresh_token = await create_refresh_token(user=user)
    content = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_type,
    }
    return JSONResponse(content=content)


@auth_router.post("/jwt/logout")
async def auth_logout(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    return {"detail": "User logged out successfully."}


@auth_router.post(
    "/jwt/refresh",
    responses={
        401: {"description": "Невалидный или просроченный refresh-токен"}
    },
)
async def auth_jwt_refresh(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> JSONResponse:
    try:
        payload = jwt.decode(
            jwt=token.credentials,
            key=settings.refresh_secret,
            algorithms=[settings.algorithm],
        )
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный или просроченный refresh-токен.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload.get("sub"))
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # TODO: Вписать в ExceptionDetails
            detail="Не удалось получить идентификатор пользователя из токена.",
        )
    user = await user_manager.get(user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или неактивен.",
        )
    access_token = await create_access_token(user=user)
    refresh_token = await create_refresh_token(user=user)
    content = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": TOKEN_TYPE,
    }
    return JSONResponse(content=content)


@user_router.get(
    "/",
    response_model=list[UserShortRead],
    description="Список пользователей в кратком виде.",
)
async def list_users(
    session: AsyncSession = Depends(get_async_session),
) -> list[UserShortRead]:
    result = await session.execute(select(User))
    users_db = result.scalars().all()
    return [UserShortRead.model_validate(obj=user_db) for user_db in users_db]


@user_router.delete(
    "/{id}",
    deprecated=True,
    description="Не используйте удаление, деактивируйте пользователей.",
)
def delete_user(id: int):
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail=ExceptionDetails.NOT_ALLOWED_REMOVE_USERS,
    )
