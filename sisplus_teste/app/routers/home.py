from __future__ import annotations
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.context import build_base_context
from app.core.db import get_conn
from app.services.menu_service import build_sidebar_items

router = APIRouter(tags=["home"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Home principal do SISPLUS.

    Responsabilidades:
    - validar se existe sessão ativa
    - buscar informações institucionais de versão/ambiente
    - identificar os menus disponíveis para o usuário com base nos papéis
    - renderizar a página inicial

    IMPORTANTE:
    - Não existe permissão fixa em código.
    - Os menus disponíveis são obtidos indiretamente pelo banco,
      através da função build_sidebar_items(roles).
    """
    session = getattr(request.state, "session", None)
    if not session:
        return RedirectResponse("/auth/login", status_code=302)

    roles = session.get("roles", []) or []

    # =========================================================
    # Menus disponíveis para o usuário
    # A fonte real disso é o banco, via menu_service -> repository
    # =========================================================
    sidebar_items = build_sidebar_items(roles)
    available_modules = [menu.get("label", "") for menu in sidebar_items if menu.get("label")]

    # =========================================================
    # Informações institucionais / versão do sistema
    # =========================================================
    ambiente = "-"
    versao = "-"
    data_atualizacao = "-"

    conn = None
    cursor = None

    try:
        conn = get_conn()
        cursor = conn.cursor()

        query = """
            SELECT sv.Nm_Ambiente,
                   sv.Cd_Versao,
                   TO_CHAR(sv.Dt_Versao, 'DD/MM/YYYY') AS dt_versao
              FROM custom.sisplus_versao sv
             WHERE sv.Sn_Ativo = 'S'
        """

        cursor.execute(query)
        row = cursor.fetchone()

        if row:
            ambiente = row[0]
            versao = row[1]
            data_atualizacao = row[2]

    except Exception:
        # Mantém fallback padrão em caso de indisponibilidade da consulta
        pass

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    now = datetime.now()

    context = build_base_context(
        request,
        page_title="Início",
        current_date=now.strftime("%d/%m/%Y"),
        last_access=now.strftime("%d/%m/%Y %H:%M"),
        role_display="Colaborador",
        company_display="Unimed Sorocaba",
        ambiente=ambiente,
        versao=versao,
        data_atualizacao=data_atualizacao,
        available_modules=available_modules,
    )

    return templates.TemplateResponse("home.html", context)