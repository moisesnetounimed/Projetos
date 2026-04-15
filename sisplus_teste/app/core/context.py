from __future__ import annotations
from datetime import datetime
from fastapi import Request
from app.core.config import settings
from app.services.menu_service import build_sidebar_items

def build_base_context(request: Request, **extra: object) -> dict[str, object]:
    session = getattr(request.state, "session", {}) or {}
    roles = session.get("roles", []) or []

    context: dict[str, object] = {
        "request": request,
        "app_title": settings.APP_TITLE,
        "app_company": settings.APP_COMPANY,
        "app_subtitle": session.get("app_subtitle", ""),
        "show_nav_actions": bool(session),
        "user": session.get("user", ""),
        "full_name": session.get("full_name", ""),
        "roles": roles,
        "sidebar_items": build_sidebar_items(roles),
        "session_ttl_minutes": settings.SESSION_TTL_MIN,
        "current_year": datetime.now().year,
    }


    #print("USUARIO:", session.get("user"))
    #print("FULL_NAME:", session.get("full_name"))
    #print("ROLES:", roles)
    #print("SIDEBAR_ITEMS:", build_sidebar_items(roles))
    
    context.update(extra)
    return context

