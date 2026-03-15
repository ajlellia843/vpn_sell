from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.auth import AdminRequired

router = APIRouter()


@router.get("/users", response_class=HTMLResponse)
async def list_users(
    request: Request,
    page: int = 1,
    limit: int = 20,
    telegram_id: str = "",
    admin: str = AdminRequired,
):
    templates = request.app.state.templates
    user_client = request.app.state.user_client
    offset = (page - 1) * limit

    users: list = []
    total = 0

    if telegram_id.strip():
        try:
            user = await user_client.get_by_telegram_id(int(telegram_id.strip()))
            users = [user]
            total = 1
        except Exception:
            users = []
            total = 0
    else:
        try:
            resp = await user_client.list_users(offset=offset, limit=limit)
            users = resp.get("items", [])
            total = resp.get("total", 0)
        except Exception:
            pass

    total_pages = max(1, (total + limit - 1) // limit)
    is_htmx = request.headers.get("HX-Request") == "true"
    template_name = "users/_table.html" if is_htmx else "users/list.html"

    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "admin": admin,
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "telegram_id": telegram_id,
        },
    )
