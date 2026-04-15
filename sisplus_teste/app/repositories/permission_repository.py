from __future__ import annotations

"""
Repositório de permissões do SISPLUS.

Responsabilidade:
- Consultar no banco de dados se um conjunto de papéis possui acesso
  a um menu ou submódulo.

IMPORTANTE:
- Este arquivo é a fonte real da validação de acesso da aplicação.
- Nenhuma permissão deve ser fixada em código Python.
- Toda regra de acesso deve estar cadastrada nas tabelas de permissão.
"""

from typing import Any

from app.core.db import get_conn


def _normalize_roles(user_roles: list[int] | list[str]) -> list[int]:
    """
    Normaliza a lista de papéis recebida da sessão.

    Comportamento:
    - converte itens numéricos para int
    - ignora valores vazios, inválidos ou não numéricos

    Exemplo:
    ['154', 258, 'abc', None] -> [154, 258]
    """
    roles: list[int] = []

    for role in user_roles:
        if str(role).strip().isdigit():
            roles.append(int(role))

    return roles


def has_menu_access(user_roles: list[int] | list[str], menu_tag: str) -> bool:
    """
    Verifica se ao menos um dos papéis informados possui acesso ao menu.

    Regras:
    - considera apenas registros ativos
    - considera permissão de consulta ativa
    - filtra pelo menu_tag informado
    """
    roles = _normalize_roles(user_roles)
    if not roles:
        return False

    bind_names = []
    bind_values: dict[str, Any] = {"menu_tag": menu_tag}

    for idx, role in enumerate(roles):
        key = f"p{idx}"
        bind_names.append(f":{key}")
        bind_values[key] = role

    sql = f"""
        SELECT DISTINCT 1
          FROM CUSTOM.SISPLUS_MENU ME
          JOIN CUSTOM.SISPLUS_MODULO MO
            ON MO.CD_MENU = ME.CD_MENU
          JOIN CUSTOM.SISPLUS_SUBMODULO SM
            ON SM.CD_MODULO = MO.CD_MODULO
          JOIN CUSTOM.SISPLUS_PERFIL_ACESSO SPA
            ON SPA.CD_SUBMODULO = SM.CD_SUBMODULO
         WHERE ME.DS_TAG_MENU = :menu_tag
           AND ME.SN_ATIVO = 'S'
           AND MO.SN_ATIVO = 'S'
           AND SM.SN_ATIVO = 'S'
           AND SM.SN_EXIBE_MENU = 'S'
           AND SPA.SN_ATIVO = 'S'
           AND SPA.SN_CONSULTAR = 'S'
           AND SPA.CD_PAPEL IN ({", ".join(bind_names)})
           AND ROWNUM = 1
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, bind_values)
        row = cur.fetchone()

    return row is not None


def has_submodule_access(user_roles: list[int] | list[str], submodule_tag: str) -> bool:
    """
    Verifica se ao menos um dos papéis informados possui acesso ao submódulo.

    Regras:
    - considera apenas registros ativos
    - considera permissão de consulta ativa
    - filtra pela tag do submódulo
    """
    roles = _normalize_roles(user_roles)
    if not roles:
        return False

    bind_names = []
    bind_values: dict[str, Any] = {"submodule_tag": submodule_tag}

    for idx, role in enumerate(roles):
        key = f"p{idx}"
        bind_names.append(f":{key}")
        bind_values[key] = role

    sql = f"""
        SELECT DISTINCT 1
          FROM CUSTOM.SISPLUS_SUBMODULO SM
          JOIN CUSTOM.SISPLUS_PERFIL_ACESSO SPA
            ON SPA.CD_SUBMODULO = SM.CD_SUBMODULO
         WHERE SM.DS_TAG_SUBMODULO = :submodule_tag
           AND SM.SN_ATIVO = 'S'
           AND SM.SN_EXIBE_MENU = 'S'
           AND SPA.SN_ATIVO = 'S'
           AND SPA.SN_CONSULTAR = 'S'
           AND SPA.CD_PAPEL IN ({", ".join(bind_names)})
           AND ROWNUM = 1
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, bind_values)
        row = cur.fetchone()

    return row is not None