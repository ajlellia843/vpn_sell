# Centralized provider: build api_gateway client (real or stub) from settings.
# Business logic uses the returned client; it does not know if real or stub.

from app.config import BotSettings
from app.services.api_client import APIClient
from shared.stubs import StubApiGatewayClient


def provide_gateway_client(settings: BotSettings):
    """Return client implementing ApiGatewayClientProtocol. Choice by use_stub_api_gateway."""
    if getattr(settings, "use_stub_api_gateway", False):
        return StubApiGatewayClient()
    return APIClient(
        base_url=settings.api_gateway_url,
        api_key=settings.service_api_key,
    )
