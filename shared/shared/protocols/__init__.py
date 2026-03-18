# Protocol definitions for switchable real/stub clients.
# Env flags: USE_STUB_API_GATEWAY, USE_STUB_USER_SERVICE, USE_STUB_BILLING_SERVICE,
# USE_STUB_VPN_SERVICE, USE_STUB_YOOKASSA, USE_STUB_XUI (see docs/stub_architecture.md).

from shared.protocols.gateway import ApiGatewayClientProtocol
from shared.protocols.user import UserServiceClientProtocol
from shared.protocols.billing import BillingServiceClientProtocol
from shared.protocols.vpn import VPNServiceClientProtocol
from shared.protocols.payment import PaymentProviderProtocol

__all__ = [
    "ApiGatewayClientProtocol",
    "UserServiceClientProtocol",
    "BillingServiceClientProtocol",
    "VPNServiceClientProtocol",
    "PaymentProviderProtocol",
]
