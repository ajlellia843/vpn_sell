# Stub implementations for switchable clients/adapters.
# Used when USE_STUB_* env flags are set; see docs/stub_architecture.md.

from shared.stubs.gateway import StubApiGatewayClient
from shared.stubs.user import StubUserServiceClient
from shared.stubs.billing import StubBillingServiceClient
from shared.stubs.vpn import StubVPNServiceClient
from shared.stubs.yookassa import StubYooKassaService

__all__ = [
    "StubApiGatewayClient",
    "StubUserServiceClient",
    "StubBillingServiceClient",
    "StubVPNServiceClient",
    "StubYooKassaService",
]
