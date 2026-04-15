from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.context import build_base_context
from app.core.permissions import require_menu_access
from app.services.menu_service import get_menu_by_tag

router = APIRouter(prefix="/contabil", tags=["contabil"])
templates = Jinja2Templates(directory="app/templates")

MENU_TAG = "contabilidade"
MENU_LABEL = "Contabilidade"


def _guard_menu(request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return RedirectResponse("/auth/login", status_code=302)

    denied = require_menu_access(request, MENU_TAG)
    if denied:
        return denied

    return session


@router.get("", response_class=HTMLResponse)
def contabil_home(request: Request):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    roles = session.get("roles", []) or []
    menu = get_menu_by_tag(roles, MENU_TAG)

    return templates.TemplateResponse(
        "menu/home.html",
        build_base_context(
            request,
            page_title=MENU_LABEL,
            module_title=MENU_LABEL,
            menu=menu or {"label": MENU_LABEL, "modules": []},
        ),
    )