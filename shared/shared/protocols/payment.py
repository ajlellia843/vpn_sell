"""Protocol for payment provider (YooKassa). Real: YooKassaService; stub: StubYooKassaService."""

from decimal import Decimal
from typing import Protocol


class PaymentProviderProtocol(Protocol):
    """Interface for payment provider: create payment and verify webhook notification."""

    async def create_payment(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
    ) -> dict[str, str]: ...

    def verify_notification(self, body: bytes, ip: str) -> dict: ...
