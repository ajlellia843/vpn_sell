from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.services.billing import BillingService
from app.services.yookassa import YooKassaService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    body = await request.body()
    ip = request.client.host if request.client else ""

    yookassa: YooKassaService = request.app.state.yookassa
    notification = yookassa.verify_notification(body, ip)

    billing = BillingService(
        session=session,
        yookassa=yookassa,
        vpn_client=request.app.state.vpn_client,
    )
    await billing.process_payment_notification(notification)

    return {"status": "ok"}
