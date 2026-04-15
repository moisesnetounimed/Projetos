from __future__ import annotations
from fastapi import Request
from fastapi.responses import RedirectResponse
from app.repositories.permission_repository import has_menu_access, has_submodule_access


def redirect_access_denied() -> RedirectResponse:
    return RedirectResponse("/acesso-negado", status_code=302)


def require_menu_access(request: Request, menu_tag: str):
    session = getattr(request.state, "session", {}) or {}
    roles = session.get("roles", []) or []

    if not has_menu_access(roles, menu_tag):
        return redirect_access_denied()

    return None


def require_submodule_access(request: Request, submodule_tag: str):
    session = getattr(request.state, "session", {}) or {}
    roles = session.get("roles", []) or []

    if not has_submodule_access(roles, submodule_tag):
        return redirect_access_denied()

    return None