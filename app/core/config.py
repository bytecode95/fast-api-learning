from functools import lru_cache
import os
from pathlib import Path
from typing import Literal, cast
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal[
    "local",
    "development",
    "test",
    "staging",
    "production",
]

# Resolve the project root independently of the terminal's working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Select the environment before creating the Settings instance.
APP_ENV = os.getenv("APP_ENV", "local").lower()

if APP_ENV not in {"local", "development", "test", "staging", "production"}:
    raise ValueError(f"Unsupported APP_ENV: {APP_ENV}")

ENV_FILES: dict[str, Path | None] = {
    "local": PROJECT_ROOT / "config/env/local.env",
    "development": PROJECT_ROOT / "config/env/development.env",
    "test": None,
    "staging": None,
    "production": None,
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES[APP_ENV],
        env_file_encoding="utf-8",
        extra="ignore",
    )
    app_env: Environment = Field(default=cast(Environment, APP_ENV), alias="APP_ENV")
    app_name: str = "Enterprise FastAPI Backend"
    api_v1_prefix: str = "/api/v1"
    secret_key: SecretStr = Field(min_length=32)
    access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    database_url: str
    cors_origins: str = ""
    aws_region: str = "ap-southeast-1"
    s3_bucket_name: str = ""
    aws_access_key_id: str | None = None
    aws_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None
    max_upload_bytes: int = Field(default=10 * 1024 * 1024, ge=1)

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
