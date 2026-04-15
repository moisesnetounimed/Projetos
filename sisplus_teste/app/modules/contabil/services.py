from __future__ import annotations
from datetime import datetime
import oracledb
from app.core.db import get_conn

def _extract_oracle_message(exc: oracledb.DatabaseError) -> str:
    detail = exc.args[0]
    message = getattr(detail, "message", str(exc))
    for marker in ("ORA-20050:", "ORA-20002:", "ORA-20001:"):
        if marker in message:
            return message.split(marker, 1)[-1].strip()
    return message.strip()



def alterar_vencimento_imposto(cd_con_pag: int, nova_data: str, motivo: str) -> dict[str, object]:
    try:
        data_convertida = datetime.strptime(nova_data, "%Y-%m-%d").date()
        sql = """
        BEGIN
            CUSTOM.PKG_APP_FINANCEIRO.Prc_Altera_Vcto_Imposto(
                pcd_con_pag => :cd_con_pag,
                pdt_imposto => :nova_data
            );
        END;
        """
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(sql, {"cd_con_pag": cd_con_pag, "nova_data": data_convertida})
            conn.commit()
        return {"sucesso": True, "erro": None}
    except ValueError:
        return {"sucesso": False, "erro": "Data inválida. Informe uma data válida."}
    except oracledb.DatabaseError as exc:
        return {"sucesso": False, "erro": _extract_oracle_message(exc)}

def excluir_zerados_reinf() -> dict[str, object]:
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            qtd_excluidos = cur.var(oracledb.NUMBER)
            cur.callproc("CUSTOM.PKG_APP_FINANCEIRO.prc_reinf_excluir_zerados", [qtd_excluidos])
            conn.commit()
        return {"sucesso": True, "qtd": int(qtd_excluidos.getvalue() or 0), "erro": None}
    except oracledb.DatabaseError as exc:
        return {"sucesso": False, "qtd": 0, "erro": _extract_oracle_message(exc)}
