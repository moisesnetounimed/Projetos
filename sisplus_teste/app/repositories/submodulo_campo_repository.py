from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def fetch_submodule_fields(cd_submodulo: int) -> list[dict[str, Any]]:
    sql = """
        SELECT CD_CAMPO,
               CD_SUBMODULO,
               NM_CAMPO,
               DS_LABEL,
               TP_CAMPO,
               DS_PLACEHOLDER,
               VL_DEFAULT,
               SN_OBRIGATORIO,
               NR_ORDEM,
               DS_MASCARA,
               DS_OPCOES,
               NM_PARAMETRO_PROC
          FROM CUSTOM.SISPLUS_SUBMODULO_CAMPO
         WHERE CD_SUBMODULO = :cd_submodulo
           AND SN_ATIVO = 'S'
         ORDER BY NR_ORDEM, DS_LABEL
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, {"cd_submodulo": cd_submodulo})
        columns = [col[0].lower() for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]