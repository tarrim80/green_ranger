from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_title: str = "Зелёный рейнджер"
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    secret: str = "SECRET"
    refresh_secret: str = "REFRESH_SECRET"
    access_token_lifetime_hours: int = 1
    refresh_token_lifetime_days: int = 30
    algorithm: str = "HS256"
    development_status: str = "PRODUCTION"
    timezone: str = "UTC"

    DEBUG: bool = development_status != "PRODUCTION"

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    class Config:
        env_file = ".env"

    @computed_field
    @property
    def access_token_lifetime_seconds(self) -> int:
        return self.access_token_lifetime_hours * 60 * 60

    @computed_field
    @property
    def refresh_token_lifetime_seconds(self) -> int:
        return self.refresh_token_lifetime_days * 24 * 60 * 60

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def media_root(self) -> Path:
        return BASE_DIR / "media"


settings = Settings()  # type: ignore
