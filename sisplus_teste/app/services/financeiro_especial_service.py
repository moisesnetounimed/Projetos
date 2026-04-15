from __future__ import annotations
import datetime as dt
import oracledb
from app.core.db import get_conn

def executar_suspensao_desconto(
    cd_matricula: str,
    dt_competencia: str,
    ids: list[str],
    usuario: str,
    motivo: str | None = None,
) -> dict[str, str | bool]:
    try:
        if not cd_matricula.strip():
            return {"ok": False, "mensagem": "Informe a matrícula."}

        if not dt_competencia.strip():
            return {"ok": False, "mensagem": "Informe a competência."}

        if not ids:
            return {"ok": False, "mensagem": "Selecione ao menos um lançamento."}

        cd_matricula_int = int(cd_matricula)
        dt_comp = dt.datetime.strptime(dt_competencia, "%Y-%m-%d").date()
        ids_int = [int(x) for x in ids]

        with get_conn() as conn:
            cur = conn.cursor()
            ids_array = conn.gettype("SYS.ODCINUMBERLIST").newobject()
            for item in ids_int:
                ids_array.append(item)

            cur.callproc(
                "CUSTOM.PKG_APP_FINANCEIRO.PRC_SUSPENDER_DESCONTO",
                [
                    cd_matricula_int,
                    dt_comp,
                    ids_array,
                    usuario,
                    motivo,
                ],
            )

        return {"ok": True, "mensagem": "Suspensão realizada com sucesso."}

    except ValueError:
        return {"ok": False, "mensagem": "Dados inválidos. Revise os campos informados."}

    except oracledb.DatabaseError as exc:
        error_obj = exc.args[0]
        mensagem = getattr(error_obj, "message", str(exc))
        return {"ok": False, "mensagem": mensagem}

    except Exception as exc:
        return {"ok": False, "mensagem": f"Erro inesperado: {exc}"}