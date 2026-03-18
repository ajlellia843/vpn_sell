"""Smoke tests for the user stub chain: StubUserServiceClient + StubApiGatewayClient.

Run with: pytest tests/test_user_stub_chain.py -v
No external services or DB required.
"""

import pytest

from shared.exceptions import NotFoundError
from shared.schemas.user import UserRead
from shared.stubs.fixtures import STUB_TELEGRAM_ID, STUB_TELEGRAM_ID_UNKNOWN, STUB_USER_ID
from shared.stubs.gateway import StubApiGatewayClient
from shared.stubs.user import StubUserServiceClient


# ── StubUserServiceClient ─────────────────────────────────────────────


@pytest.fixture
def user_client() -> StubUserServiceClient:
    return StubUserServiceClient()


class TestStubUserServiceClient:
    @pytest.mark.asyncio
    async def test_register_or_get_existing(self, user_client: StubUserServiceClient):
        """Known telegram_id returns existing user without creating a new one."""
        result = await user_client.register_or_get(STUB_TELEGRAM_ID)
        assert result["id"] == STUB_USER_ID
        assert result["telegram_id"] == STUB_TELEGRAM_ID
        # Validate against real schema
        UserRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_register_or_get_new(self, user_client: StubUserServiceClient):
        """Unknown telegram_id creates a new user."""
        result = await user_client.register_or_get(111222, "new_guy", "New")
        assert result["telegram_id"] == 111222
        assert result["username"] == "new_guy"
        assert result["id"] != STUB_USER_ID
        UserRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_found(self, user_client: StubUserServiceClient):
        result = await user_client.get_by_telegram_id(STUB_TELEGRAM_ID)
        assert result["telegram_id"] == STUB_TELEGRAM_ID
        UserRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_get_by_telegram_id_not_found(self, user_client: StubUserServiceClient):
        with pytest.raises(NotFoundError):
            await user_client.get_by_telegram_id(STUB_TELEGRAM_ID_UNKNOWN)

    @pytest.mark.asyncio
    async def test_get_user_found(self, user_client: StubUserServiceClient):
        result = await user_client.get_user(STUB_USER_ID)
        assert result["id"] == STUB_USER_ID
        UserRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_client: StubUserServiceClient):
        with pytest.raises(NotFoundError):
            await user_client.get_user("00000000-0000-0000-0000-000000000000")

    @pytest.mark.asyncio
    async def test_list_users(self, user_client: StubUserServiceClient):
        result = await user_client.list_users()
        assert "items" in result
        assert "total" in result
        assert result["total"] >= 2
        for u in result["items"]:
            UserRead.model_validate(u)

    @pytest.mark.asyncio
    async def test_update_user(self, user_client: StubUserServiceClient):
        result = await user_client.update_user(STUB_USER_ID, username="renamed")
        assert result["username"] == "renamed"
        UserRead.model_validate(result)

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_client: StubUserServiceClient):
        with pytest.raises(NotFoundError):
            await user_client.update_user("00000000-0000-0000-0000-000000000000", username="x")


# ── StubApiGatewayClient (user-related flows) ─────────────────────────


@pytest.fixture
def gw_client() -> StubApiGatewayClient:
    return StubApiGatewayClient()


class TestStubApiGatewayClient:
    @pytest.mark.asyncio
    async def test_get_me_known_user(self, gw_client: StubApiGatewayClient):
        """get_me for known telegram_id returns user + subscription."""
        result = await gw_client.get_me(STUB_TELEGRAM_ID, "stub_user", "Stub")
        assert "user" in result
        assert "subscription" in result
        assert result["user"]["telegram_id"] == STUB_TELEGRAM_ID
        UserRead.model_validate(result["user"])

    @pytest.mark.asyncio
    async def test_get_me_new_user(self, gw_client: StubApiGatewayClient):
        """get_me for unknown telegram_id registers and returns new user."""
        result = await gw_client.get_me(333444, "fresh", "Fresh")
        assert result["user"]["telegram_id"] == 333444
        UserRead.model_validate(result["user"])

    @pytest.mark.asyncio
    async def test_get_subscription_known(self, gw_client: StubApiGatewayClient):
        result = await gw_client.get_subscription(STUB_TELEGRAM_ID)
        assert "subscription" in result
        assert "vpn_access" in result

    @pytest.mark.asyncio
    async def test_get_subscription_unknown_user(self, gw_client: StubApiGatewayClient):
        """Unknown user -> NotFoundError propagates from inner user_client."""
        with pytest.raises(NotFoundError):
            await gw_client.get_subscription(STUB_TELEGRAM_ID_UNKNOWN)

    @pytest.mark.asyncio
    async def test_create_order_unknown_user(self, gw_client: StubApiGatewayClient):
        with pytest.raises(NotFoundError):
            await gw_client.create_order(STUB_TELEGRAM_ID_UNKNOWN, "some-plan")

    @pytest.mark.asyncio
    async def test_close(self, gw_client: StubApiGatewayClient):
        """close() is a no-op and does not raise."""
        await gw_client.close()
