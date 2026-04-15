from __future__ import annotations

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.context import build_base_context
from app.core.security import session_middleware, apply_session_cookie

from app.routers.auth import router as auth_router
from app.services.auth_service import authenticate_user
from app.core.session import build_session_payload
from app.routers.home import router as home_router
from app.routers.submodulo import router as submodulo_router

import jwt

app = FastAPI(title=settings.APP_TITLE)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.middleware("http")(session_middleware)

templates = Jinja2Templates(directory="app/templates")

app.include_router(submodulo_router)
app.include_router(auth_router)
app.include_router(home_router)

SECRET = "segredo"


@app.get("/login")
def legacy_login_redirect():
    return RedirectResponse("/auth/login", status_code=302)


@app.get("/logout")
def legacy_logout_redirect():
    return RedirectResponse("/auth/logout", status_code=302)


@app.get("/acesso-negado", response_class=HTMLResponse)
def access_denied(request: Request):
    if not getattr(request.state, "session", None):
        return RedirectResponse("/auth/login", status_code=302)

    return templates.TemplateResponse(
        "access_denied.html",
        build_base_context(request, page_title="Acesso negado"),
        status_code=403,
    )


@app.post("/login")
def legacy_login_post(username: str = Form(...), password: str = Form(...)):
    result = authenticate_user(username, password)

    if not result.ok:
        return RedirectResponse(
            url="/auth/login?error=1",
            status_code=302
        )

    # sessão interna do sistema atual
    payload = build_session_payload(
        user=result.username,
        full_name=result.full_name,
        roles=result.roles or [],
        app_subtitle=result.app_subtitle,
    )

    # token JWT para o outro serviço
    token = jwt.encode(
        {
            "user": result.username,
            "full_name": result.full_name,
            "roles": result.roles or [],
        },
        SECRET,
        algorithm="HS256"
    )

    # URL do outro projeto/serviço
    destino = f"http://localhost:8001/home?token={token}"

    response = RedirectResponse(url=destino, status_code=302)

    # mantém sua sessão local também
    apply_session_cookie(response, payload)

    # opcional: salva o token em cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # True em produção com HTTPS
        samesite="lax"
    )

    return response