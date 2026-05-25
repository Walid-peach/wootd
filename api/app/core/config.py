from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_env: str = "development"
    api_secret_key: str = "changeme"
    cors_origins: list[str] = ["http://localhost:4321"]

    snowflake_account: str = Field(validation_alias="DBT_SNOWFLAKE_ACCOUNT")
    snowflake_user: str = Field(validation_alias="DBT_SNOWFLAKE_USER")
    snowflake_password: str = Field(validation_alias="DBT_ENV_SECRET_SNOWFLAKE_PASSWORD")
    snowflake_role: str = Field(default="WOOTD_ADMIN", validation_alias="DBT_SNOWFLAKE_ROLE")
    snowflake_warehouse: str = Field(default="WOOTD_WH", validation_alias="DBT_SNOWFLAKE_WAREHOUSE")
    snowflake_database: str = Field(default="WOOTD_DB", validation_alias="DBT_SNOWFLAKE_DATABASE")

    snowflake_raw_schema: str = Field(default="RAW", validation_alias="DBT_SNOWFLAKE_SCHEMA")
    snowflake_marts_schema: str = "MARTS"
    sentry_dsn: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: Any) -> list[str] | Any:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()  # type: ignore[call-arg]
