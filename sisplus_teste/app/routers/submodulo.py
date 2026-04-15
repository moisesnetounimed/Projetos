from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.context import build_base_context
from app.core.permissions import require_submodule_access
from app.repositories.submodulo_repository import fetch_submodule_by_tag
from app.repositories.submodulo_campo_repository import fetch_submodule_fields
from app.services.submodulo_service import processar_submodulo_generico

router = APIRouter(prefix="/app/submodulo", tags=["submodulo"])
templates = Jinja2Templates(directory="app/templates")


def _render_submodulo(
    request: Request,
    submodulo: dict,
    campos: list[dict],
    sucesso: str | None = None,
    erro: str | None = None,
    form_data: dict | None = None,
):
    context = build_base_context(
        request,
        page_title=submodulo.get("nm_submodulo", "Submódulo"),
        module_title=submodulo.get("nm_modulo", ""),
        submodule=submodulo,
        campos=campos,
        sucesso=sucesso,
        erro=erro,
        form_data=form_data or {},
    )

    nm_template = (submodulo.get("nm_template") or "").strip()
    tp_abertura = (submodulo.get("tp_abertura") or "").strip().upper()
    tp_tela = (submodulo.get("tp_tela") or "").strip().upper()

    if tp_abertura == "ROTA" and nm_template:
        return templates.TemplateResponse(nm_template, context)

    if tp_abertura == "GENERICA":
        if tp_tela == "ACAO_SIMPLES":
            return templates.TemplateResponse("submodulo/acao_simples.html", context)

        if tp_tela == "FORM_SIMPLES":
            return templates.TemplateResponse("submodulo/form_simples.html", context)

    return templates.TemplateResponse("submodulo/default.html", context)


@router.get("/{tag}", response_class=HTMLResponse)
def abrir_submodulo(tag: str, request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return RedirectResponse("/auth/login", status_code=302)

    denied = require_submodule_access(request, tag)
    if denied:
        return denied

    submodulo = fetch_submodule_by_tag(tag)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    campos = fetch_submodule_fields(submodulo["cd_submodulo"])

    return _render_submodulo(
        request=request,
        submodulo=submodulo,
        campos=campos,
    )


@router.post("/{tag}", response_class=HTMLResponse)
async def executar_submodulo(tag: str, request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return RedirectResponse("/auth/login", status_code=302)

    denied = require_submodule_access(request, tag)
    if denied:
        return denied

    submodulo = fetch_submodule_by_tag(tag)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    campos = fetch_submodule_fields(submodulo["cd_submodulo"])
    form = await request.form()
    form_data = {k: str(v) for k, v in form.items()}

    retorno = processar_submodulo_generico(
        submodulo=submodulo,
        campos=campos,
        form_data=form_data,
        usuario=session.get("user", ""),
    )

    return _render_submodulo(
        request=request,
        submodulo=submodulo,
        campos=campos,
        sucesso=retorno["mensagem"] if retorno["ok"] else None,
        erro=retorno["mensagem"] if not retorno["ok"] else None,
        form_data=form_data,
    )