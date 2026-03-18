# Centralized providers: build vpn client and payment provider (real or stub) from settings.
# BillingService receives these via constructor; it does not know if real or stub.

from shared.clients.vpn import VPNServiceClient
from shared.stubs import StubVPNServiceClient, StubYooKassaService

from app.config import BillingServiceSettings
from app.services.yookassa import YooKassaService


def provide_vpn_client(settings: BillingServiceSettings) -> VPNServiceClient | StubVPNServiceClient:
    if settings.use_stub_vpn_service:
        return StubVPNServiceClient()
    return VPNServiceClient(
        base_url=settings.vpn_service_url,
        service_api_key=settings.service_api_key,
    )


def provide_payment_provider(settings: BillingServiceSettings) -> YooKassaService | StubYooKassaService:
    if settings.use_stub_yookassa:
        return StubYooKassaService()
    return YooKassaService(
        shop_id=settings.yookassa_shop_id,
        secret_key=settings.yookassa_secret_key,
        return_url=settings.yookassa_return_url,
        webhook_secret=settings.yookassa_webhook_secret,
    )
