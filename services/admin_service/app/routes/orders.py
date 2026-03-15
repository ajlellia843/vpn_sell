from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.auth import AdminRequired

router = APIRouter()


@router.get("/orders", response_class=HTMLResponse)
async def list_orders(
    request: Request,
    page: int = 1,
    limit: int = 20,
    status: str = "",
    admin: str = AdminRequired,
):
    templates = request.app.state.templates
    billing_client = request.app.state.billing_client
    offset = (page - 1) * limit

    orders: list = []
    total = 0

    try:
        resp = await billing_client.list_orders(
            offset=offset, limit=limit, status=status or None
        )
        orders = resp.get("items", [])
        total = resp.get("total", 0)
    except Exception:
        pass

    total_pages = max(1, (total + limit - 1) // limit)
    is_htmx = request.headers.get("HX-Request") == "true"
    template_name = "orders/_table.html" if is_htmx else "orders/list.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "admin": admin,
            "orders": orders,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "status": status,
        },
    )
