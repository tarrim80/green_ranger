from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    exceptions,
    schemas,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import jwt_strategy
from app.core.config import settings
from app.core.db import get_async_session
from app.models import User
from app.schemas import UserCreate


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """Провайдер репозитория пользователей для зависимостей FastAPI."""
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """Возвращает сконфигурированную JWT-стратегию."""
    return jwt_strategy


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей, расширяющий функциональность FastAPI-Users."""

    def __init__(self, user_db, session: AsyncSession):
        super().__init__(user_db=user_db)
        self.session = session

    reset_password_token_secret = settings.secret
    verification_token_secret = settings.secret

    async def create(
        self,
        user_create: schemas.BaseUserCreate,
        safe: bool = False,
        request: Request | None = None,
    ) -> User:
        """Создает нового пользователя с дополнительной логикой."""
        if not isinstance(user_create, UserCreate):
            return await super().create(user_create, safe, request)

        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = user_create.model_dump()
        user_dict.pop("role", None)
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        self.session.add(created_user)
        await self.session.commit()
        await self.session.refresh(created_user)

        return created_user

    async def validate_password(
        self,
        password: str,
        user: schemas.BaseUserCreate | User,
    ) -> None:
        """Проверяет пароль на соответствие внутренним правилам."""
        if len(password) < 3:
            raise exceptions.InvalidPasswordException(
                reason="Password should be at least 3 characters"
            )
        if user.email in password:
            raise exceptions.InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

    async def on_after_register(
        self, user: User, request: Request | None = None
    ):
        """Выполняет действия после успешной регистрации пользователя."""
        # TODO: Logging
        print(f"Пользователь {user.email} зарегистрирован.")
        await self.session.refresh(user, ["role"])


async def get_user_manager(
    user_db=Depends(get_user_db),
    session: AsyncSession = Depends(get_async_session),
):
    """Провайдер менеджера пользователей для зависимостей FastAPI."""
    yield UserManager(user_db=user_db, session=session)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
