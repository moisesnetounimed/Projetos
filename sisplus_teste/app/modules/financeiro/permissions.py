from __future__ import annotations

"""
Camada de apoio para controle de acesso da aplicação.

IMPORTANTE:
- As permissões NÃO são definidas neste arquivo.
- As permissões são mantidas no banco de dados.
- Este módulo apenas:
    1. lê os papéis (roles) da sessão do usuário
    2. consulta o repositório de permissões
    3. devolve a resposta HTTP adequada quando não houver acesso

Fluxo resumido:
Request -> sessão -> roles -> repository -> validação no banco -> redirect/continuação
"""

from fastapi import Request
from fastapi.responses import RedirectResponse

from app.repositories.permission_repository import (
    has_menu_access,
    has_submodule_access,
)


def redirect_access_denied() -> RedirectResponse:
    """
    Retorna o redirect padrão para a página de acesso negado.
    """
    return RedirectResponse("/acesso-negado", status_code=302)


def _get_roles_from_request(request: Request) -> list[int] | list[str]:
    """
    Extrai os papéis (roles) da sessão atual.

    Observações:
    - A autenticação grava os papéis na sessão do usuário.
    - Esses papéis são usados como entrada para a consulta de permissão no banco.
    - Se não houver sessão ou papéis, retorna lista vazia.
    """
    session = getattr(request.state, "session", {}) or {}
    return session.get("roles", []) or []


def require_menu_access(request: Request, menu_tag: str):
    """
    Valida se o usuário possui acesso ao menu informado.

    Parâmetros:
    - request: requisição atual do FastAPI
    - menu_tag: tag lógica do menu (ex.: 'financeiro', 'contabilidade', 'operacoes')

    Retorno:
    - None, se o acesso for permitido
    - RedirectResponse('/acesso-negado'), se o acesso for negado

    Observação:
    - A validação efetiva é feita no banco via permission_repository.has_menu_access().
    """
    roles = _get_roles_from_request(request)

    if not has_menu_access(roles, menu_tag):
        return redirect_access_denied()

    return None


def require_submodule_access(request: Request, submodule_tag: str):
    """
    Valida se o usuário possui acesso ao submódulo informado.

    Parâmetros:
    - request: requisição atual do FastAPI
    - submodule_tag: tag lógica do submódulo
      (ex.: 'alterardatavencimentoimposto_fin', 'ajustarrateio_cont')

    Retorno:
    - None, se o acesso for permitido
    - RedirectResponse('/acesso-negado'), se o acesso for negado

    Observação:
    - A validação efetiva é feita no banco via permission_repository.has_submodule_access().
    """
    roles = _get_roles_from_request(request)

    if not has_submodule_access(roles, submodule_tag):
        return redirect_access_denied()

    return None