from shared.config import BaseServiceSettings


class GatewaySettings(BaseServiceSettings):
    service_name: str = "api-gateway"
    user_service_url: str = "http://user-service:8000"
    billing_service_url: str = "http://billing-service:8000"
    vpn_service_url: str = "http://vpn-service:8000"

    # Stubs (env: USE_STUB_USER_SERVICE, USE_STUB_BILLING_SERVICE, USE_STUB_VPN_SERVICE)
    use_stub_user_service: bool = False
    use_stub_billing_service: bool = False
    use_stub_vpn_service: bool = False
