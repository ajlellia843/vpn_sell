from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import AdminRequired

router = APIRouter()


@router.get("/plans", response_class=HTMLResponse)
async def list_plans(request: Request, admin: str = AdminRequired):
    templates = request.app.state.templates
    billing_client = request.app.state.billing_client

    plans: list = []
    try:
        plans = await billing_client.list_plans()
    except Exception:
        pass

    return templates.TemplateResponse(
        "plans/list.html",
        {"request": request, "admin": admin, "plans": plans},
    )


@router.get("/plans/new", response_class=HTMLResponse)
async def new_plan(request: Request, admin: str = AdminRequired):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "plans/form.html",
        {"request": request, "admin": admin, "plan": None},
    )


@router.post("/plans")
async def create_plan(request: Request, admin: str = AdminRequired):
    billing_client = request.app.state.billing_client
    form = await request.form()

    data = {
        "name": form.get("name"),
        "duration_days": int(form.get("duration_days", 30)),
        "price": str(form.get("price", "0")),
        "currency": form.get("currency", "RUB"),
        "description": form.get("description") or None,
        "traffic_limit_gb": int(form["traffic_limit_gb"]) if form.get("traffic_limit_gb") else None,
        "device_limit": int(form.get("device_limit", 1)),
        "is_active": form.get("is_active") == "on",
    }

    await billing_client.create_plan(data)
    return RedirectResponse(url="/plans", status_code=302)


@router.get("/plans/{plan_id}/edit", response_class=HTMLResponse)
async def edit_plan(request: Request, plan_id: str, admin: str = AdminRequired):
    templates = request.app.state.templates
    billing_client = request.app.state.billing_client

    plan = await billing_client.get_plan(plan_id)
    return templates.TemplateResponse(
        "plans/form.html",
        {"request": request, "admin": admin, "plan": plan},
    )


@router.post("/plans/{plan_id}")
async def update_plan(request: Request, plan_id: str, admin: str = AdminRequired):
    billing_client = request.app.state.billing_client
    form = await request.form()

    data = {
        "name": form.get("name"),
        "duration_days": int(form.get("duration_days", 30)),
        "price": str(form.get("price", "0")),
        "currency": form.get("currency", "RUB"),
        "description": form.get("description") or None,
        "traffic_limit_gb": int(form["traffic_limit_gb"]) if form.get("traffic_limit_gb") else None,
        "device_limit": int(form.get("device_limit", 1)),
        "is_active": form.get("is_active") == "on",
    }

    await billing_client.update_plan(plan_id, data)
    return RedirectResponse(url="/plans", status_code=302)
