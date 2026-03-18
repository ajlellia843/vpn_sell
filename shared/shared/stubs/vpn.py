"""Stub implementation of VPNServiceClientProtocol."""

from typing import Any

from shared.stubs.fixtures import stub_vpn_access


class StubVPNServiceClient:
    """Returns minimal fixture data for vpn_service. No HTTP calls."""

    async def provision(
        self,
        subscription_id: str,
        user_id: str,
        plan_duration_days: int,
        traffic_limit_gb: int | None = None,
        device_limit: int = 1,
    ) -> dict[str, Any]:
        return {
            "subscription_id": subscription_id,
            "provision_status": "provisioned",
            "connection_uri": "vless://stub@stub.example:443",
        }

    async def extend(self, subscription_id: str, days: int) -> dict[str, Any]:
        return {
            "subscription_id": subscription_id,
            "provision_status": "provisioned",
            "connection_uri": None,
        }

    async def disable(self, subscription_id: str) -> dict[str, Any]:
        return {}

    async def enable(self, subscription_id: str) -> dict[str, Any]:
        return {}

    async def get_access(self, subscription_id: str) -> dict[str, Any]:
        return stub_vpn_access(subscription_id=subscription_id)

    async def close(self) -> None:
        pass
