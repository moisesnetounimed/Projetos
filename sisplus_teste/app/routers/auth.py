from __future__ import annotations
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.core.context import build_base_context
from app.core.security import apply_session_cookie
from app.core.session import build_session_payload, touch_session
from app.services.auth_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if getattr(request.state, "session", None):
        return RedirectResponse(url="/", status_code=302)

    reason = request.query_params.get("reason")
    message = None
    if reason == "expired":
        message = "Sua sessão expirou por inatividade. Faça login novamente."
    elif request.query_params.get("error") == "1":
        message = "Usuário ou senha inválidos."

    return templates.TemplateResponse(
        "login.html",
        build_base_context(request, error=message),
    )


@router.post("/login", response_class=HTMLResponse)
def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    result = authenticate_user(username, password)
    if not result.ok:
        return templates.TemplateResponse(
            "login.html",
            build_base_context(request, error=result.message),
            status_code=401,
        )

    payload = build_session_payload(
        user=result.username,
        full_name=result.full_name,
        roles=result.roles or [],
        app_subtitle=result.app_subtitle,
    )

    response = RedirectResponse(url="/", status_code=302)
    apply_session_cookie(response, payload)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/auth/login", status_code=302)
    response.delete_cookie(settings.SESSION_COOKIE)
    return response


@router.post("/heartbeat")
def heartbeat(request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return JSONResponse({"ok": False}, status_code=401)

    response = JSONResponse({"ok": True})
    apply_session_cookie(response, touch_session(session))
    return response
