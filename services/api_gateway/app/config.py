from shared.config import BaseServiceSettings


class GatewaySettings(BaseServiceSettings):
    service_name: str = "api-gateway"
    user_service_url: str = "http://user-service:8000"
    billing_service_url: str = "http://billing-service:8000"
    vpn_service_url: str = "http://vpn-service:8000"
