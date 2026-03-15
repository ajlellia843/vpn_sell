import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from shared.clients.vpn import VPNServiceClient
from shared.exceptions import NotFoundError
from shared.schemas.order import OrderStatus

from app.metrics import ACTIVE_SUBSCRIPTIONS, PAYMENTS_TOTAL
from app.models.order import Order
from app.models.subscription import Subscription
from app.repositories.order import OrderRepository
from app.repositories.plan import PlanRepository
from app.repositories.subscription import SubscriptionRepository
from app.services.yookassa import YooKassaService

logger = structlog.get_logger()


class BillingService:
    def __init__(
        self,
        session: AsyncSession,
        yookassa: YooKassaService,
        vpn_client: VPNServiceClient,
    ) -> None:
        self._session = session
        self._yookassa = yookassa
        self._vpn = vpn_client
        self._plans = PlanRepository(session)
        self._orders = OrderRepository(session)
        self._subs = SubscriptionRepository(session)

    async def create_order(self, user_id: uuid.UUID, plan_id: uuid.UUID) -> Order:
        plan = await self._plans.get_by_id(plan_id)
        if plan is None or not plan.is_active:
            raise NotFoundError("Plan not found or inactive")

        order = await self._orders.create(
            user_id=user_id,
            plan_id=plan_id,
            amount=plan.price,
            currency=plan.currency,
        )

        payment = await self._yookassa.create_payment(
            order_id=str(order.id),
            amount=plan.price,
            currency=plan.currency,
            description=f"VPN plan: {plan.name}",
        )

        order.payment_url = payment["confirmation_url"]
        order.external_payment_id = payment["payment_id"]
        await self._session.flush()
        await self._session.refresh(order)
        await self._session.commit()
        return order

    async def process_payment_notification(self, notification: dict) -> None:
        payment_id = notification.get("id")
        status = notification.get("status")

        if not payment_id:
            logger.warning("payment_notification_missing_id")
            return

        order = await self._orders.get_by_external_payment_id(payment_id)
        if order is None:
            logger.warning("payment_notification_unknown_order", payment_id=payment_id)
            return

        if order.status == OrderStatus.PAID:
            return

        order.provider_payload = notification

        if status == "succeeded":
            order.status = OrderStatus.PAID
            await self._session.flush()

            plan = await self._plans.get_by_id(order.plan_id)
            now = datetime.now(timezone.utc)
            sub = await self._subs.create(
                user_id=order.user_id,
                plan_id=order.plan_id,
                order_id=order.id,
                start_at=now,
                end_at=now + timedelta(days=plan.duration_days),
            )

            try:
                await self._vpn.provision(
                    subscription_id=str(sub.id),
                    user_id=str(order.user_id),
                    plan_duration_days=plan.duration_days,
                    traffic_limit_gb=plan.traffic_limit_gb,
                    device_limit=plan.device_limit,
                )
                sub.auto_provisioned = True
                await self._session.flush()
            except Exception:
                logger.exception(
                    "vpn_provision_failed", subscription_id=str(sub.id)
                )

            PAYMENTS_TOTAL.labels(status="succeeded").inc()
            ACTIVE_SUBSCRIPTIONS.inc()

        elif status == "canceled":
            order.status = OrderStatus.CANCELLED
            PAYMENTS_TOTAL.labels(status="cancelled").inc()

        else:
            order.status = OrderStatus.FAILED
            PAYMENTS_TOTAL.labels(status="failed").inc()

        await self._session.commit()

    async def extend_subscription(
        self, subscription_id: uuid.UUID, days: int
    ) -> Subscription:
        sub = await self._subs.extend_subscription(subscription_id, days)
        if sub is None:
            raise NotFoundError("Subscription not found")

        try:
            await self._vpn.extend(str(subscription_id), days)
        except Exception:
            logger.exception(
                "vpn_extend_failed", subscription_id=str(subscription_id)
            )

        await self._session.commit()
        return sub

    async def revoke_subscription(self, subscription_id: uuid.UUID) -> Subscription:
        sub = await self._subs.get_by_id(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found")

        sub.status = "cancelled"
        await self._session.flush()
        await self._session.refresh(sub)

        try:
            await self._vpn.disable(str(subscription_id))
        except Exception:
            logger.exception(
                "vpn_disable_failed", subscription_id=str(subscription_id)
            )

        ACTIVE_SUBSCRIPTIONS.dec()
        await self._session.commit()
        return sub
