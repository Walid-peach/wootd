from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_env: str = "development"
    api_secret_key: str = "changeme"
    cors_origins: list[str] = ["http://localhost:4321"]

    r2_endpoint_url: str
    r2_access_key_id: str
    r2_secret_access_key: str
    r2_bucket_name: str = "wootd-lakehouse"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    database_url: str = ""
    sentry_dsn: str = ""

    mlflow_tracking_uri: str = "http://localhost:5000"


settings = Settings()  # type: ignore[call-arg]
