"""Stub implementation of AbstractVPNPanelAdapter for vpn_service (USE_STUB_XUI)."""

from app.adapters.base import AbstractVPNPanelAdapter


class StubXUIAdapter(AbstractVPNPanelAdapter):
    """No-op 3x-ui adapter; returns minimal data. No HTTP to panel."""

    def __init__(self, inbound_id: int = 1) -> None:
        self._inbound_id = inbound_id

    @property
    def inbound_id(self) -> int:
        return self._inbound_id

    async def authenticate(self) -> None:
        pass

    async def create_client(
        self,
        client_id: str,
        email: str,
        total_gb: int,
        expiry_days: int,
        device_limit: int,
    ) -> dict:
        return {"id": client_id}

    async def get_client(self, client_id: str) -> dict | None:
        return {"id": client_id, "expiryTime": 0}

    async def extend_client(self, client_id: str, days: int) -> dict:
        return {"id": client_id}

    async def disable_client(self, client_id: str) -> None:
        pass

    async def enable_client(self, client_id: str) -> None:
        pass

    async def get_client_link(self, client_id: str, inbound_id: int) -> str:
        return f"vless://{client_id}@stub.example:443"

    async def close(self) -> None:
        pass  # no-op for stub; matches XUIAdapter.close() for lifespan
