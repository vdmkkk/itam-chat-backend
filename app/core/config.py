from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",  # ignore unrelated env vars like POSTGRES_*, DOMAIN, ACME_EMAIL
    )

    # App
    APP_PORT: int = 8000
    DEV: bool = True

    # JWT
    JWT_SECRET: str = Field("change_me_in_prod", description="Secret key for signing JWTs")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_MINUTES: int = 60

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@db:5432/itam_chat"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


class PaginationParams(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="Max items to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")


