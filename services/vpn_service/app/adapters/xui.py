import base64
import json
import time
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from shared.logging import get_logger

from app.adapters.base import AbstractVPNPanelAdapter

logger = get_logger(__name__)


class XUIAdapter(AbstractVPNPanelAdapter):
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        inbound_id: int = 1,
        timeout: float = 15.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._username = username
        self._password = password
        self._inbound_id_value = inbound_id
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=timeout)
        self._authenticated = False

    @property
    def inbound_id(self) -> int:
        return self._inbound_id_value

    async def authenticate(self) -> None:
        resp = await self._client.post(
            "/login",
            data={"username": self._username, "password": self._password},
        )
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            raise RuntimeError(f"XUI login failed: {body.get('msg', 'unknown error')}")
        self._authenticated = True
        logger.info("xui_authenticated")

    async def _ensure_auth(self) -> None:
        if not self._authenticated:
            await self.authenticate()

    async def _request(self, method: str, path: str, **kwargs: Any) -> dict:
        await self._ensure_auth()
        resp = await self._client.request(method, path, **kwargs)
        if resp.status_code == 401:
            self._authenticated = False
            await self.authenticate()
            resp = await self._client.request(method, path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def create_client(
        self,
        client_id: str,
        email: str,
        total_gb: int,
        expiry_days: int,
        device_limit: int,
    ) -> dict:
        total_bytes = total_gb * (1024 ** 3) if total_gb > 0 else 0
        expiry_ms = int((time.time() + expiry_days * 86400) * 1000)

        settings = json.dumps({
            "clients": [{
                "id": client_id,
                "email": email,
                "totalGB": total_bytes,
                "expiryTime": expiry_ms,
                "limitIp": device_limit,
                "enable": True,
            }],
        })

        return await self._request(
            "POST",
            "/panel/api/inbounds/addClient",
            json={"id": self._inbound_id_value, "settings": settings},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def get_client(self, client_id: str) -> dict | None:
        try:
            result = await self._request(
                "GET", f"/panel/api/inbounds/getClientTraffics/{client_id}",
            )
            obj = result.get("obj")
            if not result.get("success") or obj is None:
                return None
            return obj
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def extend_client(self, client_id: str, days: int) -> dict:
        client = await self.get_client(client_id)
        current_expiry = client.get("expiryTime", 0) if client else 0
        base_ms = max(current_expiry, int(time.time() * 1000))
        new_expiry = base_ms + days * 86_400_000

        settings = json.dumps({
            "clients": [{"id": client_id, "expiryTime": new_expiry}],
        })

        return await self._request(
            "POST",
            f"/panel/api/inbounds/updateClient/{client_id}",
            json={"id": self._inbound_id_value, "settings": settings},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def disable_client(self, client_id: str) -> None:
        settings = json.dumps({
            "clients": [{"id": client_id, "enable": False}],
        })
        await self._request(
            "POST",
            f"/panel/api/inbounds/updateClient/{client_id}",
            json={"id": self._inbound_id_value, "settings": settings},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def enable_client(self, client_id: str) -> None:
        settings = json.dumps({
            "clients": [{"id": client_id, "enable": True}],
        })
        await self._request(
            "POST",
            f"/panel/api/inbounds/updateClient/{client_id}",
            json={"id": self._inbound_id_value, "settings": settings},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), reraise=True)
    async def get_client_link(self, client_id: str, inbound_id: int) -> str:
        result = await self._request(
            "GET", f"/panel/api/inbounds/get/{inbound_id}",
        )
        if not result.get("success"):
            raise RuntimeError(f"Failed to fetch inbound {inbound_id}")

        inbound = result["obj"]
        protocol = inbound.get("protocol", "vless")
        listen_addr = inbound.get("listen", "") or self._base_url.split("://")[-1].split(":")[0]
        port = inbound.get("port", 443)
        stream = json.loads(inbound.get("streamSettings", "{}"))
        network = stream.get("network", "tcp")
        security = stream.get("security", "tls")
        remark = inbound.get("remark", "vpn")

        if protocol == "vless":
            return (
                f"vless://{client_id}@{listen_addr}:{port}"
                f"?type={network}&security={security}#{remark}"
            )

        if protocol == "vmess":
            vmess_obj = {
                "v": "2",
                "ps": remark,
                "add": listen_addr,
                "port": str(port),
                "id": client_id,
                "net": network,
                "tls": security,
            }
            encoded = base64.urlsafe_b64encode(
                json.dumps(vmess_obj).encode(),
            ).decode()
            return f"vmess://{encoded}"

        raise RuntimeError(f"Unsupported protocol: {protocol}")

    async def close(self) -> None:
        await self._client.aclose()
