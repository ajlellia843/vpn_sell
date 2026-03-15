from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.auth import AdminRequired, create_access_token, verify_password

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    templates = request.app.state.templates
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request):
    settings = request.app.state.settings
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")

    if username != settings.admin_username or not verify_password(
        str(password), settings.admin_password_hash
    ):
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=401,
        )

    token = create_access_token(
        data={"sub": username},
        secret=settings.admin_jwt_secret,
        algorithm=settings.jwt_algorithm,
        expires_minutes=settings.jwt_expire_minutes,
    )
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("admin_token")
    return response


@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, admin: str = AdminRequired):
    templates = request.app.state.templates
    user_client = request.app.state.user_client
    billing_client = request.app.state.billing_client

    total_users = 0
    active_subscriptions = 0
    total_orders = 0
    recent_orders: list = []

    try:
        users_resp = await user_client.list_users(offset=0, limit=1)
        total_users = users_resp.get("total", 0)
    except Exception:
        pass

    try:
        subs_resp = await billing_client.list_subscriptions(offset=0, limit=1, status="active")
        active_subscriptions = subs_resp.get("total", 0)
    except Exception:
        pass

    try:
        orders_resp = await billing_client.list_orders(offset=0, limit=10)
        total_orders = orders_resp.get("total", 0)
        recent_orders = orders_resp.get("items", [])
    except Exception:
        pass

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "admin": admin,
            "total_users": total_users,
            "active_subscriptions": active_subscriptions,
            "total_orders": total_orders,
            "recent_orders": recent_orders,
        },
    )
