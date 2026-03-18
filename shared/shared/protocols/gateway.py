"""Protocol for bot_service -> api_gateway client. Real: APIClient; stub: StubApiGatewayClient."""

from typing import Any, Protocol


class ApiGatewayClientProtocol(Protocol):
    """Interface for the client used by bot to call api_gateway (BFF)."""

    async def get_me(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> dict[str, Any]: ...

    async def get_plans(self) -> list[dict[str, Any]]: ...

    async def create_order(self, telegram_id: int, plan_id: str) -> dict[str, Any]: ...

    async def get_order(self, order_id: str) -> dict[str, Any]: ...

    async def get_subscription(self, telegram_id: int) -> dict[str, Any]: ...

    async def extend_subscription(self, telegram_id: int, days: int) -> dict[str, Any]: ...

    async def close(self) -> None: ...
