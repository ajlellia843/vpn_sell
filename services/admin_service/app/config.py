from shared.config import BaseServiceSettings


class AdminServiceSettings(BaseServiceSettings):
    service_name: str = "admin-service"

    user_service_url: str
    billing_service_url: str
    vpn_service_url: str

    admin_username: str = "admin"
    admin_password_hash: str
    admin_jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
