import ipaddress
import json
import uuid
from decimal import Decimal

import httpx
import structlog

from shared.exceptions import ValidationError

logger = structlog.get_logger()

_YOOKASSA_TRUSTED: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network("185.71.76.0/27"),
    ipaddress.ip_network("185.71.77.0/27"),
    ipaddress.ip_network("77.75.153.0/25"),
    ipaddress.ip_network("77.75.156.11/32"),
    ipaddress.ip_network("77.75.156.35/32"),
    ipaddress.ip_network("77.75.154.128/25"),
    ipaddress.ip_network("2a02:5180::/32"),
]

API_URL = "https://api.yookassa.ru/v3"


class YooKassaService:
    def __init__(
        self,
        shop_id: str,
        secret_key: str,
        return_url: str,
        webhook_secret: str = "",
    ) -> None:
        self._shop_id = shop_id
        self._secret_key = secret_key
        self._return_url = return_url
        self._webhook_secret = webhook_secret

    async def create_payment(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
    ) -> dict[str, str]:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_URL}/payments",
                auth=(self._shop_id, self._secret_key),
                headers={"Idempotence-Key": str(uuid.uuid4())},
                json={
                    "amount": {"value": str(amount), "currency": currency},
                    "confirmation": {
                        "type": "redirect",
                        "return_url": self._return_url,
                    },
                    "capture": True,
                    "description": description,
                    "metadata": {"order_id": order_id},
                },
            )
            resp.raise_for_status()
            data = resp.json()

        return {
            "payment_id": data["id"],
            "confirmation_url": data["confirmation"]["confirmation_url"],
        }

    def verify_notification(self, body: bytes, ip: str) -> dict:
        addr = ipaddress.ip_address(ip)
        trusted = any(addr in net for net in _YOOKASSA_TRUSTED)
        if not trusted:
            logger.warning("yookassa_untrusted_ip", ip=ip)
            raise ValidationError(f"Untrusted source IP: {ip}")

        notification = json.loads(body)
        return notification.get("object", notification)
