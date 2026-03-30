from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_asyncpg_scheme(cls, v: str) -> str:
        # Railway PostgreSQL addon entrega postgresql://, asyncpg requiere postgresql+asyncpg://
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    TEST_DATABASE_URL: str | None = None
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"

    # API keys para el fallback chain de generación de resúmenes.
    # Opcionales en Settings: los clientes SDK las leen directo del env en tiempo de request.
    # En producción deben estar seteadas; si no, SummarizerUnavailableError en el primer POST.
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
