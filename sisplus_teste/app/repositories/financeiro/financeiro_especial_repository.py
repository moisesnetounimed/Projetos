from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def buscar_lancamentos_suspensao(cd_matricula: int, dt_competencia: str) -> list[dict[str, Any]]:
    sql = """
       Select  u.cd_usuario_ac_dc
              ,u.cd_matricula
              ,u.cd_lcto_mensalidade || ' - ' || lm.ds_lcto_mensalidade As lancamento
              ,u.dt_competencia
              ,u.vl_nominal
              ,u.sn_suspenso
              ,u.ds_observacao
        From  dbaps.usuario_ac_dc    u
             ,dbaps.lcto_mensalidade lm
          Where u.cd_lcto_mensalidade = lm.cd_lcto_mensalidade
          And u.cd_matricula = :cd_matricula
          And trunc(u.dt_competencia) = to_date(:dt_competencia, 'YYYY-MM-DD')
          Order By u.cd_usuario_ac_dc
    """

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            sql,
            {
                "cd_matricula": cd_matricula,
                "dt_competencia": dt_competencia,
            },
        )
        columns = [col[0].lower() for col in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]