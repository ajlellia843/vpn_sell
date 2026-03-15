import httpx
from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/yookassa")
async def yookassa_webhook(request: Request) -> Response:
    billing_url: str = request.app.state.billing_service_url
    body = await request.body()
    content_type = request.headers.get("content-type", "application/json")

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{billing_url.rstrip('/')}/webhooks/yookassa",
            content=body,
            headers={"Content-Type": content_type},
        )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )
