from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def fetch_sidebar_rows(user_roles: list[int] | list[str]) -> list[dict[str, Any]]:
    roles = [int(r) for r in user_roles if str(r).strip().isdigit()]
    if not roles:
        return []

    bind_names = []
    bind_values: dict[str, Any] = {}

    for idx, role in enumerate(roles):
        key = f"p{idx}"
        bind_names.append(f":{key}")
        bind_values[key] = role

    sql = f"""
        SELECT DISTINCT
               ME.CD_MENU,
               ME.NM_MENU,
               ME.DS_TAG_MENU,
               ME.DS_ICONE            AS ICONE_MENU,
               ME.NR_ORDEM            AS ORDEM_MENU,
               MO.CD_MODULO,
               MO.NM_MODULO,
               MO.DS_TAG_MODULO,
               MO.DS_ICONE            AS ICONE_MODULO,
               MO.NR_ORDEM            AS ORDEM_MODULO,
               SM.CD_SUBMODULO,
               SM.NM_SUBMODULO,
               SM.DS_TAG_SUBMODULO,
               SM.DS_DESCRICAO,
               SM.DS_ROTA,
               SM.TP_ABERTURA,
               SM.TP_TELA,
               SM.DS_ICONE            AS ICONE_SUBMODULO,
               SM.NR_ORDEM            AS ORDEM_SUBMODULO
          FROM CUSTOM.SISPLUS_MENU ME
          JOIN CUSTOM.SISPLUS_MODULO MO
            ON MO.CD_MENU = ME.CD_MENU
          JOIN CUSTOM.SISPLUS_SUBMODULO SM
            ON SM.CD_MODULO = MO.CD_MODULO
          JOIN CUSTOM.SISPLUS_PERFIL_ACESSO SPA
            ON SPA.CD_SUBMODULO = SM.CD_SUBMODULO
         WHERE ME.SN_ATIVO = 'S'
           AND MO.SN_ATIVO = 'S'
           AND SM.SN_ATIVO = 'S'
           AND SM.SN_EXIBE_MENU = 'S'
           AND SPA.SN_ATIVO = 'S'
           AND SPA.SN_CONSULTAR = 'S'
           AND SPA.CD_PAPEL IN ({", ".join(bind_names)})
         ORDER BY ME.NR_ORDEM, MO.NR_ORDEM, SM.NR_ORDEM, SM.NM_SUBMODULO
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, bind_values)
        columns = [col[0].lower() for col in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

    return rows