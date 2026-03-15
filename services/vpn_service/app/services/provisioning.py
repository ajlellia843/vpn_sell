import time
import uuid

from prometheus_client import Counter, Histogram
from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import NotFoundError
from shared.logging import get_logger
from shared.schemas.vpn_access import (
    ProvisionRequest,
    ProvisionResponse,
    ProvisionStatus,
)

from app.adapters.base import AbstractVPNPanelAdapter
from app.models.vpn_access import VPNAccessBinding
from app.repositories.vpn_access import VPNAccessRepository

logger = get_logger(__name__)

PROVISION_ATTEMPTS = Counter(
    "provision_attempts_total",
    "Total provision attempts",
    ["status"],
)

PROVISION_DURATION = Histogram(
    "provision_duration_seconds",
    "Time spent provisioning VPN access",
)


class ProvisioningService:
    def __init__(self, session: AsyncSession, adapter: AbstractVPNPanelAdapter) -> None:
        self._session = session
        self._adapter = adapter
        self._repo = VPNAccessRepository(session)

    async def provision(self, request: ProvisionRequest) -> ProvisionResponse:
        start = time.perf_counter()

        existing = await self._repo.get_by_subscription_id(request.subscription_id)

        if existing and existing.provision_status == ProvisionStatus.PROVISIONED:
            return ProvisionResponse(
                subscription_id=existing.subscription_id,
                provision_status=ProvisionStatus.PROVISIONED,
                connection_uri=existing.connection_uri,
            )

        if existing and existing.provision_status == ProvisionStatus.FAILED:
            binding = existing
            binding.retry_count += 1
            binding.provision_status = ProvisionStatus.PENDING
            binding.last_error = None
        elif existing:
            binding = existing
        else:
            binding = await self._repo.create(
                subscription_id=request.subscription_id,
                provision_status=ProvisionStatus.PENDING,
            )

        client_id = str(uuid.uuid4())
        email = f"sub-{request.subscription_id}"

        try:
            await self._adapter.create_client(
                client_id=client_id,
                email=email,
                total_gb=request.traffic_limit_gb or 0,
                expiry_days=request.plan_duration_days,
                device_limit=request.device_limit,
            )

            link = await self._adapter.get_client_link(
                client_id=client_id,
                inbound_id=self._adapter.inbound_id,
            )

            binding.xui_client_id = client_id
            binding.inbound_id = self._adapter.inbound_id
            binding.connection_uri = link
            binding.provision_status = ProvisionStatus.PROVISIONED

            await self._session.commit()

            PROVISION_ATTEMPTS.labels(status="success").inc()
            PROVISION_DURATION.observe(time.perf_counter() - start)

            return ProvisionResponse(
                subscription_id=binding.subscription_id,
                provision_status=ProvisionStatus.PROVISIONED,
                connection_uri=binding.connection_uri,
            )

        except Exception as exc:
            binding.provision_status = ProvisionStatus.FAILED
            binding.last_error = str(exc)
            await self._session.commit()

            PROVISION_ATTEMPTS.labels(status="failure").inc()
            PROVISION_DURATION.observe(time.perf_counter() - start)

            logger.error(
                "provision_failed",
                subscription_id=str(request.subscription_id),
                error=str(exc),
            )
            raise

    async def extend(self, subscription_id: uuid.UUID, days: int) -> ProvisionResponse:
        binding = await self._repo.get_by_subscription_id(subscription_id)
        if not binding:
            raise NotFoundError(f"No VPN binding for subscription {subscription_id}")

        await self._adapter.extend_client(binding.xui_client_id, days)
        await self._session.commit()

        return ProvisionResponse(
            subscription_id=binding.subscription_id,
            provision_status=ProvisionStatus(binding.provision_status),
            connection_uri=binding.connection_uri,
        )

    async def disable(self, subscription_id: uuid.UUID) -> None:
        binding = await self._repo.get_by_subscription_id(subscription_id)
        if not binding:
            raise NotFoundError(f"No VPN binding for subscription {subscription_id}")

        await self._adapter.disable_client(binding.xui_client_id)
        binding.provision_status = ProvisionStatus.DISABLED
        await self._session.commit()

    async def enable(self, subscription_id: uuid.UUID) -> None:
        binding = await self._repo.get_by_subscription_id(subscription_id)
        if not binding:
            raise NotFoundError(f"No VPN binding for subscription {subscription_id}")

        await self._adapter.enable_client(binding.xui_client_id)
        binding.provision_status = ProvisionStatus.PROVISIONED
        await self._session.commit()

    async def get_access(self, subscription_id: uuid.UUID) -> VPNAccessBinding:
        binding = await self._repo.get_by_subscription_id(subscription_id)
        if not binding:
            raise NotFoundError(f"No VPN binding for subscription {subscription_id}")
        return binding
