from __future__ import annotations

"""
MENU SERVICE - SIDEBAR DINÂMICA (SISPLUS)

Responsabilidade:
-----------------
Construir a estrutura da sidebar com base nos papéis (roles) do usuário,
utilizando dados vindos do banco.

⚠️ IMPORTANTE:
- NÃO existe regra fixa de permissão aqui
- NÃO existe role hardcoded
- Tudo vem do banco ()

Fluxo:
------
roles → repository → estrutura → sidebar renderizada
"""

from typing import Any, Iterable

from app.repositories.menu_repository import fetch_sidebar_rows


def build_sidebar_items(roles: Iterable[int | str]) -> list[dict[str, Any]]:
    """
    Monta a sidebar completa baseada nos papéis do usuário.

    Parâmetros:
        roles: lista de papéis do usuário (session)

    Retorno:
        Lista estruturada de menus com módulos e submódulos
    """

    rows = fetch_sidebar_rows(roles)

    menus: dict[int, dict[str, Any]] = {}

    for row in rows:
        cd_menu = row["cd_menu"]
        cd_modulo = row["cd_modulo"]

        # =========================
        # MENU (NÍVEL 1)
        # =========================
        if cd_menu not in menus:
            menus[cd_menu] = {
                "label": format_label(row["nm_menu"]),
                "tag": row["ds_tag_menu"],
                "icon": row.get("icone_menu") or "circle",
                "order": row.get("ordem_menu") or 0,
                "modules": {},
            }

        # =========================
        # MÓDULO (NÍVEL 2)
        # =========================
        if cd_modulo not in menus[cd_menu]["modules"]:
            menus[cd_menu]["modules"][cd_modulo] = {
                "label": format_label(row["nm_modulo"]),
                "tag": row["ds_tag_modulo"],
                "icon": row.get("icone_modulo") or "square",
                "order": row.get("ordem_modulo") or 0,
                "submodules": [],
            }

        # =========================
        # SUBMÓDULO (NÍVEL 3)
        # =========================
        menus[cd_menu]["modules"][cd_modulo]["submodules"].append(
            {
                "label": format_label(row["nm_submodulo"]),
                "tag": row["ds_tag_submodulo"],
                "description": row.get("ds_descricao") or "",
                "route": row.get("ds_rota") or "#",
                "icon": row.get("icone_submodulo") or "dot",
                "order": row.get("ordem_submodulo") or 0,
            }
        )

    # =========================
    # CONVERSÃO FINAL
    # =========================
    result = []

    for menu in menus.values():
        modules = list(menu["modules"].values())

        # Ordena módulos
        modules.sort(key=lambda m: m["order"])

        # Ordena submódulos
        for mod in modules:
            mod["submodules"].sort(key=lambda s: s["order"])

        menu["modules"] = modules
        result.append(menu)

    # Ordena menus
    result.sort(key=lambda m: m["order"])

    return result


def format_label(text: str) -> str:
    """
    Padroniza texto para exibição.

    Exemplo:
        'CONTABILIDADE' → 'Contabilidade'
    """
    if not text:
        return ""

    return text.strip().capitalize()