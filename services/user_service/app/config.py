from shared.config import BaseServiceSettings


class UserServiceSettings(BaseServiceSettings):
    service_name: str = "user-service"
    DB_SCHEMA: str = "users"
