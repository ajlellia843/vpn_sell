from shared.config import BaseServiceSettings


class AdminServiceSettings(BaseServiceSettings):
    service_name: str = "admin-service"

    user_service_url: str
    billing_service_url: str
    vpn_service_url: str

    # Stubs (env: USE_STUB_USER_SERVICE, USE_STUB_BILLING_SERVICE, USE_STUB_VPN_SERVICE)
    use_stub_user_service: bool = False
    use_stub_billing_service: bool = False
    use_stub_vpn_service: bool = False

    admin_username: str = "admin"
    admin_password_hash: str
    admin_jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
