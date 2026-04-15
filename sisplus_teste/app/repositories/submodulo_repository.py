from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def fetch_submodule_by_tag(tag: str) -> dict[str, Any] | None:
    sql = """
        SELECT SM.CD_SUBMODULO,
               SM.NM_SUBMODULO,
               SM.DS_TAG_SUBMODULO,
               SM.DS_DESCRICAO,
               SM.DS_ROTA,
               SM.TP_ABERTURA,
               SM.TP_TELA,
               SM.NM_TEMPLATE,
               SM.DS_PROCEDURE,
               SM.DS_ICONE,
               SM.NR_ORDEM,
               MO.CD_MODULO,
               MO.NM_MODULO,
               MO.DS_TAG_MODULO,
               ME.CD_MENU,
               ME.NM_MENU,
               ME.DS_TAG_MENU
          FROM CUSTOM.SISPLUS_SUBMODULO SM
          JOIN CUSTOM.SISPLUS_MODULO MO
            ON MO.CD_MODULO = SM.CD_MODULO
          JOIN CUSTOM.SISPLUS_MENU ME
            ON ME.CD_MENU = MO.CD_MENU
         WHERE LOWER(TRIM(SM.DS_TAG_SUBMODULO)) = LOWER(TRIM(:tag))
           AND SM.SN_ATIVO = 'S'
           AND MO.SN_ATIVO = 'S'
           AND ME.SN_ATIVO = 'S'
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, {"tag": tag})
        row = cur.fetchone()

        if not row:
            return None

        columns = [col[0].lower() for col in cur.description]
        return dict(zip(columns, row))