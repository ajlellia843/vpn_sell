from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "unknown"
    service_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    db_url: str = "postgresql+asyncpg://vpn:vpn@postgres:5432/vpn_platform"
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10

    service_api_key: str = "change-me-in-production"

    host: str = "0.0.0.0"
    port: int = 8000
