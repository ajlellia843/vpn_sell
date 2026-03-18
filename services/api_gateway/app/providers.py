# Centralized providers: build user, billing, vpn clients (real or stub) from settings.
# Routes use request.app.state.*_client; they do not know if real or stub.

from shared.clients.billing import BillingServiceClient
from shared.clients.user import UserServiceClient
from shared.clients.vpn import VPNServiceClient
from shared.stubs import StubBillingServiceClient, StubUserServiceClient, StubVPNServiceClient

from app.config import GatewaySettings


def provide_user_client(settings: GatewaySettings) -> UserServiceClient | StubUserServiceClient:
    if settings.use_stub_user_service:
        return StubUserServiceClient()
    return UserServiceClient(
        base_url=settings.user_service_url,
        service_api_key=settings.service_api_key,
    )


def provide_billing_client(settings: GatewaySettings) -> BillingServiceClient | StubBillingServiceClient:
    if settings.use_stub_billing_service:
        return StubBillingServiceClient()
    return BillingServiceClient(
        base_url=settings.billing_service_url,
        service_api_key=settings.service_api_key,
    )


def provide_vpn_client(settings: GatewaySettings) -> VPNServiceClient | StubVPNServiceClient:
    if settings.use_stub_vpn_service:
        return StubVPNServiceClient()
    return VPNServiceClient(
        base_url=settings.vpn_service_url,
        service_api_key=settings.service_api_key,
    )
