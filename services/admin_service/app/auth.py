from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, secret: str, algorithm: str, expires_minutes: int) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_token(token: str, secret: str, algorithm: str) -> dict:
    return jwt.decode(token, secret, algorithms=[algorithm])


def get_current_admin(request: Request) -> str:
    token = request.cookies.get("admin_token")
    if not token:
        raise _redirect_to_login()

    settings = request.app.state.settings
    try:
        payload = decode_token(token, settings.admin_jwt_secret, settings.jwt_algorithm)
        username: str | None = payload.get("sub")
        if username is None:
            raise _redirect_to_login()
        return username
    except jwt.PyJWTError:
        raise _redirect_to_login()


class _LoginRedirectException(Exception):
    pass


def _redirect_to_login() -> _LoginRedirectException:
    return _LoginRedirectException()


async def login_redirect_handler(request: Request, exc: _LoginRedirectException) -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=302)


AdminRequired = Depends(get_current_admin)
