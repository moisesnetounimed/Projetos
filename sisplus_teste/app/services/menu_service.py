from __future__ import annotations
from typing import Any
from app.repositories.menu_repository import fetch_sidebar_rows


def build_sidebar_items(user_roles: list[int] | list[str]) -> list[dict[str, Any]]:
    rows = fetch_sidebar_rows(user_roles)
    menus: dict[int, dict[str, Any]] = {}

    for row in rows:
        cd_menu = row["cd_menu"]
        cd_modulo = row["cd_modulo"]

        if cd_menu not in menus:
            menus[cd_menu] = {
                "cd_menu": cd_menu,
                "label": format_label(row["nm_menu"]),
                "tag": row["ds_tag_menu"],
                "icon": row.get("icone_menu") or "",
                "order": row.get("ordem_menu") or 0,
                "modules": {},
            }

        if cd_modulo not in menus[cd_menu]["modules"]:
            menus[cd_menu]["modules"][cd_modulo] = {
                "cd_modulo": cd_modulo,
                "label": format_label(row["nm_modulo"]),
                "tag": row["ds_tag_modulo"],
                "icon": row.get("icone_modulo") or "",
                "order": row.get("ordem_modulo") or 0,
                "submodules": [],
            }

        menus[cd_menu]["modules"][cd_modulo]["submodules"].append(
            {
                "cd_submodulo": row["cd_submodulo"],
                "label": format_label(row["nm_submodulo"]),
                "tag": row["ds_tag_submodulo"],
                "description": row.get("ds_descricao") or "",
                "route": row.get("ds_rota") or "#",
                "open_type": row.get("tp_abertura") or "ROTA",
                "screen_type": row.get("tp_tela") or "",
                "icon": row.get("icone_submodulo") or "",
                "order": row.get("ordem_submodulo") or 0,
            }
        )

    result = []
    for menu in menus.values():
        menu["modules"] = list(menu["modules"].values())
        result.append(menu)

    return result

def format_label(text: str) -> str:
    if not text:
        return ""
    return text.capitalize()

def get_menu_by_tag(user_roles: list[int] | list[str], menu_tag: str) -> dict[str, Any] | None:
    menus = build_sidebar_items(user_roles)

    for menu in menus:
        if menu.get("tag") == menu_tag:
            return menu

    return None