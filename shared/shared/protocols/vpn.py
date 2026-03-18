"""Protocol for vpn_service HTTP client. Real: VPNServiceClient; stub: StubVPNServiceClient."""

from typing import Any, Protocol


class VPNServiceClientProtocol(Protocol):
    """Interface for vpn_service client (provision, extend, disable, enable, get_access)."""

    async def provision(
        self,
        subscription_id: str,
        user_id: str,
        plan_duration_days: int,
        traffic_limit_gb: int | None = None,
        device_limit: int = 1,
    ) -> dict[str, Any]: ...

    async def extend(self, subscription_id: str, days: int) -> dict[str, Any]: ...

    async def disable(self, subscription_id: str) -> dict[str, Any]: ...

    async def enable(self, subscription_id: str) -> dict[str, Any]: ...

    async def get_access(self, subscription_id: str) -> dict[str, Any]: ...

    async def close(self) -> None: ...
