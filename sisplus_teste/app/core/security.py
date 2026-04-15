from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.core.config import settings
from app.core.session import decode_session, encode_session, is_session_expired, should_touch_session, touch_session

PUBLIC_PATH_PREFIXES = (
    "/static",
    "/auth/login",
    "/favicon.ico",
)
PUBLIC_EXACT_PATHS = {"/auth/login", "/auth/logout"}



def is_public_path(path: str) -> bool:
    return path in PUBLIC_EXACT_PATHS or path.startswith(PUBLIC_PATH_PREFIXES)



def logout_response(reason: str = "", redirect_to: str = "/auth/login"):
    location = redirect_to
    if reason:
        sep = "&" if "?" in redirect_to else "?"
        location = f"{redirect_to}{sep}reason={reason}"
    response = RedirectResponse(location, status_code=302)
    response.delete_cookie(settings.SESSION_COOKIE)
    return response



def unauthorized_json(reason: str = "expired") -> JSONResponse:
    response = JSONResponse({"ok": False, "reason": reason}, status_code=401)
    response.delete_cookie(settings.SESSION_COOKIE)
    return response



def get_authenticated_session(request: Request) -> dict | None:
    return getattr(request.state, "session", None)



def require_authenticated_user(request: Request) -> dict:
    session = get_authenticated_session(request)
    if not session:
        raise PermissionError("Usuário não autenticado.")
    return session



def apply_session_cookie(response, session_data: dict) -> None:
    response.set_cookie(
        settings.SESSION_COOKIE,
        encode_session(session_data),
        httponly=True,
        samesite="lax",
        secure=settings.SECURE_COOKIES,
        max_age=settings.SESSION_TTL_MIN * 60,
    )


async def session_middleware(request: Request, call_next):
    path = request.url.path
    token = request.cookies.get(settings.SESSION_COOKIE, "") or ""
    session = decode_session(token)

    request.state.session = None
    request.state.session_should_refresh = False

    if session:
        if is_session_expired(session):
            if path == "/auth/heartbeat":
                return unauthorized_json("expired")
            if not is_public_path(path):
                return logout_response("expired")
        else:
            request.state.session = session
            request.state.session_should_refresh = should_touch_session(session)

    response = await call_next(request)

    current_session = getattr(request.state, "session", None)
    if current_session and getattr(request.state, "session_should_refresh", False):
        apply_session_cookie(response, touch_session(current_session))

    return response
