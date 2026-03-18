from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "bot-service"
    bot_token: str
    bot_mode: str = "polling"
    webhook_url: str = ""
    api_gateway_url: str = "http://api-gateway:8000"
    service_api_key: str = "change-me"

    # Stub: use stub instead of real api_gateway client (env: USE_STUB_API_GATEWAY)
    use_stub_api_gateway: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8080
