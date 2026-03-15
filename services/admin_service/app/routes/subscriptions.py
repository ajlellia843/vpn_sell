from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import AdminRequired

router = APIRouter()


@router.get("/subscriptions", response_class=HTMLResponse)
async def list_subscriptions(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    admin: str = AdminRequired,
):
    templates = request.app.state.templates
    billing_client = request.app.state.billing_client
    offset = (page - 1) * limit

    subscriptions: list = []
    total = 0

    try:
        resp = await billing_client.list_subscriptions(
            offset=offset, limit=limit, status=status or None
        )
        subscriptions = resp.get("items", [])
        total = resp.get("total", 0)
    except Exception:
        pass

    total_pages = max(1, (total + limit - 1) // limit)
    is_htmx = request.headers.get("HX-Request") == "true"
    template_name = "subscriptions/_table.html" if is_htmx else "subscriptions/list.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "admin": admin,
            "subscriptions": subscriptions,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "status": status,
        },
    )


@router.post("/subscriptions/{sub_id}/extend")
async def extend_subscription(request: Request, sub_id: str, admin: str = AdminRequired):
    billing_client = request.app.state.billing_client
    form = await request.form()
    days = int(form.get("days", 30))

    await billing_client.extend_subscription(sub_id, days)
    return RedirectResponse(url="/subscriptions", status_code=302)


@router.post("/subscriptions/{sub_id}/revoke")
async def revoke_subscription(request: Request, sub_id: str, admin: str = AdminRequired):
    billing_client = request.app.state.billing_client

    await billing_client.revoke_subscription(sub_id)
    return RedirectResponse(url="/subscriptions", status_code=302)
