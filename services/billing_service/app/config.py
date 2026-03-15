from shared.config import BaseServiceSettings


class BillingServiceSettings(BaseServiceSettings):
    service_name: str = "billing-service"
    vpn_service_url: str
    yookassa_shop_id: str
    yookassa_secret_key: str
    yookassa_return_url: str
    yookassa_webhook_secret: str = ""
