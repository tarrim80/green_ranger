from fastapi_users.authentication.strategy.jwt import JWTStrategy

from app.core.config import settings
from app.models import User

jwt_strategy = JWTStrategy(
    secret=settings.secret,
    lifetime_seconds=settings.access_token_lifetime_seconds,
    token_audience=["fastapi-users:auth"],
    algorithm=settings.algorithm,
)

refresh_jwt_strategy = JWTStrategy(
    secret=settings.refresh_secret,
    lifetime_seconds=settings.refresh_token_lifetime_seconds,
    token_audience=["fastapi-users:refresh"],
    algorithm=settings.algorithm,
)


async def create_access_token(user: User) -> str:
    """Создает токен доступа для пользователя."""
    return await jwt_strategy.write_token(user)


async def create_refresh_token(user: User) -> str:
    """Создает токен обновления для пользователя."""
    return await refresh_jwt_strategy.write_token(user)
