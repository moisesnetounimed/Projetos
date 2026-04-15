from __future__ import annotations
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.context import build_base_context
from app.core.permissions import require_menu_access
from app.repositories.financeiro.financeiro_especial_repository import buscar_lancamentos_suspensao
from app.repositories.financeiro.financeiro_rateio_repository import buscar_conpag_rateio
from app.repositories.submodulo_repository import fetch_submodule_by_tag
from app.services.financeiro_especial_service import executar_suspensao_desconto
from app.services.financeiro_rateio_service import salvar_e_processar_rateio
from app.services.menu_service import get_menu_by_tag

router = APIRouter(prefix="/financeiro", tags=["financeiro"])
templates = Jinja2Templates(directory="app/templates")

MENU_TAG = "financeiro"
MENU_LABEL = "Financeiro"

TAG_SUSPENDER_DESCONTO = "suspenderdescontousuario"
TAG_AJUSTAR_RATEIO = "ajustarrateio_fin"  # ajuste aqui se no banco estiver como 'ajustarrateio'


def _guard_menu(request: Request):
    session = getattr(request.state, "session", None)
    if not session:
        return RedirectResponse("/auth/login", status_code=302)

    denied = require_menu_access(request, MENU_TAG)
    if denied:
        return denied

    return session


@router.get("", response_class=HTMLResponse)
def financeiro_home(request: Request):
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


def _render_suspender_desconto(
    request: Request,
    submodulo: dict,
    resultados=None,
    sucesso: str | None = None,
    erro: str | None = None,
    form_data: dict | None = None,
):
    return templates.TemplateResponse(
        "financeiro/suspender_desconto_usuario.html",
        build_base_context(
            request,
            page_title=submodulo.get("nm_submodulo", "Suspender desconto"),
            module_title=MENU_LABEL,
            submodule=submodulo,
            resultados=resultados,
            sucesso=sucesso,
            erro=erro,
            form_data=form_data or {},
        ),
    )


@router.get("/suspender-desconto", response_class=HTMLResponse)
def suspender_desconto_home(request: Request):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_SUSPENDER_DESCONTO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    return _render_suspender_desconto(
        request=request,
        submodulo=submodulo,
        resultados=None,
    )


@router.post("/suspender-desconto/pesquisar", response_class=HTMLResponse)
def suspender_desconto_pesquisar(
    request: Request,
    cd_matricula: str = Form(...),
    dt_competencia: str = Form(...),
):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_SUSPENDER_DESCONTO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    try:
        resultados = buscar_lancamentos_suspensao(
            cd_matricula=int(cd_matricula),
            dt_competencia=dt_competencia,
        )

        return _render_suspender_desconto(
            request=request,
            submodulo=submodulo,
            resultados=resultados,
            form_data={
                "cd_matricula": cd_matricula,
                "dt_competencia": dt_competencia,
            },
        )

    except Exception as exc:
        return _render_suspender_desconto(
            request=request,
            submodulo=submodulo,
            resultados=[],
            erro=f"Erro ao pesquisar lançamentos: {exc}",
            form_data={
                "cd_matricula": cd_matricula,
                "dt_competencia": dt_competencia,
            },
        )


@router.post("/suspender-desconto/executar", response_class=HTMLResponse)
async def suspender_desconto_executar(request: Request):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_SUSPENDER_DESCONTO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    form = await request.form()
    cd_matricula = str(form.get("cd_matricula", ""))
    dt_competencia = str(form.get("dt_competencia", ""))
    motivo = str(form.get("motivo", ""))
    ids = form.getlist("ids")

    retorno = executar_suspensao_desconto(
        cd_matricula=cd_matricula,
        dt_competencia=dt_competencia,
        ids=ids,
        usuario=session.get("user", ""),
        motivo=motivo,
    )

    resultados = (
        buscar_lancamentos_suspensao(
            cd_matricula=int(cd_matricula),
            dt_competencia=dt_competencia,
        )
        if cd_matricula and dt_competencia
        else []
    )

    return _render_suspender_desconto(
        request=request,
        submodulo=submodulo,
        resultados=resultados,
        sucesso=retorno["mensagem"] if retorno["ok"] else None,
        erro=retorno["mensagem"] if not retorno["ok"] else None,
        form_data={
            "cd_matricula": cd_matricula,
            "dt_competencia": dt_competencia,
            "motivo": motivo,
        },
    )


def _render_rateio_conpag(
    request: Request,
    submodulo: dict,
    conpag=None,
    rateios=None,
    sucesso: str | None = None,
    erro: str | None = None,
    form_data: dict | None = None,
):
    return templates.TemplateResponse(
        "financeiro/alterar_rateio_conpag.html",
        build_base_context(
            request,
            page_title=submodulo.get("nm_submodulo", "Alteração de Rateio"),
            module_title=MENU_LABEL,
            submodule=submodulo,
            conpag=conpag,
            rateios=rateios,
            sucesso=sucesso,
            erro=erro,
            form_data=form_data or {},
        ),
    )


@router.get("/rateio-conpag", response_class=HTMLResponse)
def rateio_conpag_home(request: Request):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_AJUSTAR_RATEIO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    return _render_rateio_conpag(
        request=request,
        submodulo=submodulo,
        conpag=None,
        rateios=None,
    )


@router.post("/rateio-conpag/pesquisar", response_class=HTMLResponse)
def rateio_conpag_pesquisar(
    request: Request,
    cd_con_pag: str = Form(...),
):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_AJUSTAR_RATEIO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    try:
        resultado = buscar_conpag_rateio(int(cd_con_pag))
        if not resultado:
            return _render_rateio_conpag(
                request=request,
                submodulo=submodulo,
                conpag=None,
                rateios=[],
                erro="Conta a pagar não encontrada.",
                form_data={"cd_con_pag": cd_con_pag},
            )

        return _render_rateio_conpag(
            request=request,
            submodulo=submodulo,
            conpag=resultado["conpag"],
            rateios=resultado["rateios"],
            form_data={"cd_con_pag": cd_con_pag},
        )

    except Exception as exc:
        return _render_rateio_conpag(
            request=request,
            submodulo=submodulo,
            conpag=None,
            rateios=[],
            erro=f"Erro ao pesquisar rateio: {exc}",
            form_data={"cd_con_pag": cd_con_pag},
        )


@router.post("/rateio-conpag/salvar", response_class=HTMLResponse)
async def rateio_conpag_salvar(request: Request):
    session = _guard_menu(request)
    if not isinstance(session, dict):
        return session

    submodulo = fetch_submodule_by_tag(TAG_AJUSTAR_RATEIO)
    if not submodulo:
        return RedirectResponse("/acesso-negado", status_code=302)

    form = await request.form()

    cd_con_pag = str(form.get("cd_con_pag", ""))
    motivo = str(form.get("motivo", ""))

    cds_setor = form.getlist("cd_setor")
    cds_item_res = form.getlist("cd_item_res")
    cds_reduzido = form.getlist("cd_reduzido")
    dts_competencia = form.getlist("dt_competencia")
    vls_rateio = form.getlist("vl_rateio")

    itens = []
    total_linhas = max(
        len(cds_setor),
        len(cds_item_res),
        len(cds_reduzido),
        len(dts_competencia),
        len(vls_rateio),
    )

    for i in range(total_linhas):
        item = {
            "cd_setor": cds_setor[i] if i < len(cds_setor) else "",
            "cd_item_res": cds_item_res[i] if i < len(cds_item_res) else "",
            "cd_reduzido": cds_reduzido[i] if i < len(cds_reduzido) else "",
            "dt_competencia": dts_competencia[i] if i < len(dts_competencia) else "",
            "vl_rateio": vls_rateio[i] if i < len(vls_rateio) else "",
        }

        if any(str(v).strip() for v in item.values()):
            itens.append(item)

    retorno = salvar_e_processar_rateio(
        cd_con_pag=cd_con_pag,
        motivo=motivo,
        usuario=session.get("user", ""),
        itens=itens,
    )

    resultado = buscar_conpag_rateio(int(cd_con_pag)) if cd_con_pag.strip().isdigit() else None

    return _render_rateio_conpag(
        request=request,
        submodulo=submodulo,
        conpag=resultado["conpag"] if resultado else None,
        rateios=resultado["rateios"] if resultado else [],
        sucesso=retorno["mensagem"] if retorno["ok"] else None,
        erro=retorno["mensagem"] if not retorno["ok"] else None,
        form_data={
            "cd_con_pag": cd_con_pag,
            "motivo": motivo,
        },
    )