from __future__ import annotations

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.core.Authentication import get_url_sistema
from app.core.security import session_middleware, apply_session_cookie
from app.services.auth_service import authenticate_user
from app.core.session import build_session_payload, touch_session
from app.core.config import Settings
import jwt

app = FastAPI(title=settings.APP_TITLE)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.middleware("http")(session_middleware)

templates = Jinja2Templates(directory="app/templates")

SECRET = Settings.SECRET_KEY

@app.get("/")
def login_redirect_raiz():
    
    return RedirectResponse("/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    if getattr(request.state, "session", None):
     response = RedirectResponse(url="/login", status_code=302)
     response.delete_cookie(settings.SESSION_COOKIE)
     return response
    
    reason = request.query_params.get("reason")
    message = None

    if reason == "expired":
        message = "Sua sessão expirou por inatividade. Faça login novamente."
    elif request.query_params.get("error") == "1":
        message = "Usuário ou senha inválidos."
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "message": message
        }
    )


@app.get("/logout")
def logout_redirect():
    response.delete_cookie(settings.SESSION_COOKIE)
    response = RedirectResponse("/login", status_code=302)
   
    return response

@app.get("/acesso-negado", response_class=HTMLResponse)
def accesso_negado(request: Request):
    if not getattr(request.state, "session", None):
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse(
        "access_denied.html",
        request, page_title="Acesso negado",
        status_code=403,
    )

app.post("/heartbeat")
def heartbeat(request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return JSONResponse({"ok": False}, status_code=401)

    response = JSONResponse({"ok": True})
    apply_session_cookie(response, touch_session(session))
    return response
@app.post("/login", response_class=HTMLResponse)
def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    result = authenticate_user(username, password)
    if not result.ok:
      return templates.TemplateResponse(
    "login.html",
    {
        "request": request,
        "message": "Usuário ou Senha Inválidos"
    },
    status_code=401,
)

    payload = build_session_payload(
        user=result.username,
        full_name=result.full_name,
        roles=result.roles or [],
        app_subtitle=result.app_subtitle,
    )

   # response = RedirectResponse(url="/", status_code=302)
   # apply_session_cookie(response, payload)

    # sessão interna do sistema atual

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
    urlbase = get_url_sistema(url="base")
    destino = f"{urlbase}?token={token}"

    print("URL DESTINO", destino)
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