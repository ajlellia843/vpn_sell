"""Stub implementation of PaymentProviderProtocol (YooKassa)."""

from decimal import Decimal

from shared.stubs.fixtures import STUB_ORDER_ID


class StubYooKassaService:
    """Returns minimal fixture data for payments; accepts any webhook body. No HTTP to YooKassa."""

    async def create_payment(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
    ) -> dict[str, str]:
        return {
            "payment_id": "stub-payment-id",
            "confirmation_url": "https://stub.example/confirm",
        }

    def verify_notification(self, body: bytes, ip: str) -> dict:
        import json
        data = json.loads(body) if body else {}
        obj = data.get("object", data)
        return obj if isinstance(obj, dict) else {"id": "stub", "status": "succeeded"}
