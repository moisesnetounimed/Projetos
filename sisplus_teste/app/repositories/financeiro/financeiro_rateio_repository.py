from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def buscar_conpag_rateio(cd_con_pag: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT CPP.CD_CON_PAG,
                   CPP.VL_MOEDA
              FROM DBAMV.CON_PAG CPP
             WHERE CPP.CD_CON_PAG = :cd_con_pag
            """,
            {"cd_con_pag": cd_con_pag},
        )
        row = cur.fetchone()
        if not row:
            return None

        conpag = {
            "cd_con_pag": row[0],
            "vl_moeda": row[1],
        }

        cur.execute(
            """
            SELECT RP.CD_RATCON_PAG,
                   RP.CD_CON_PAG,
                   RP.CD_SETOR,
                   RP.VL_RATEIO,
                   RP.DT_COMPETENCIA,
                   TO_CHAR(RP.DT_COMPETENCIA, 'DD/MM/YYYY') AS DT_COMPETENCIA_FMT,
                   RP.CD_ITEM_RES AS CONTA_CUSTO,
                   RP.CD_REDUZIDO AS CONTA_CONTABIL
              FROM DBAMV.RATCON_PAG RP
             WHERE RP.CD_CON_PAG = :cd_con_pag
             ORDER BY RP.CD_RATCON_PAG
            """,
            {"cd_con_pag": cd_con_pag},
        )
        cols = [c[0].lower() for c in cur.description]
        rateios = [dict(zip(cols, r)) for r in cur.fetchall()]

    return {
        "conpag": conpag,
        "rateios": rateios,
    }