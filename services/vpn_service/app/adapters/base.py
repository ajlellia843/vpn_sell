from abc import ABC, abstractmethod


class AbstractVPNPanelAdapter(ABC):
    @property
    @abstractmethod
    def inbound_id(self) -> int: ...

    @abstractmethod
    async def authenticate(self) -> None: ...

    @abstractmethod
    async def create_client(
        self,
        client_id: str,
        email: str,
        total_gb: int,
        expiry_days: int,
        device_limit: int,
    ) -> dict: ...

    @abstractmethod
    async def get_client(self, client_id: str) -> dict | None: ...

    @abstractmethod
    async def extend_client(self, client_id: str, days: int) -> dict: ...

    @abstractmethod
    async def disable_client(self, client_id: str) -> None: ...

    @abstractmethod
    async def enable_client(self, client_id: str) -> None: ...

    @abstractmethod
    async def get_client_link(self, client_id: str, inbound_id: int) -> str: ...
