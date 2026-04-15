from __future__ import annotations
import datetime as dt
from typing import Any
import oracledb
from app.repositories.procedure_executor_repository import execute_named_procedure


def _convert_field_value(tp_campo: str, raw_value: str | None) -> Any:
    if raw_value is None:
        return None

    value = raw_value.strip()
    if value == "":
        return None

    tp = (tp_campo or "").upper()

    if tp == "NUMBER":
        return int(value)

    if tp == "DATE":
        return dt.datetime.strptime(value, "%Y-%m-%d").date()

    return value


def processar_submodulo_generico(
    submodulo: dict[str, Any],
    campos: list[dict[str, Any]],
    form_data: dict[str, str],
    usuario: str,
) -> dict[str, str | bool]:
    try:
        procedure_name = (submodulo.get("ds_procedure") or "").strip()
        if not procedure_name:
            return {"ok": False, "mensagem": "Submódulo sem procedure configurada."}

        params: dict[str, Any] = {}

        for campo in campos:
            nm_campo = campo.get("nm_campo")
            nm_parametro_proc = campo.get("nm_parametro_proc")
            tp_campo = campo.get("tp_campo") or "TEXT"
            obrigatorio = (campo.get("sn_obrigatorio") or "N") == "S"

            if not nm_campo or not nm_parametro_proc:
                continue

            raw_value = form_data.get(nm_campo, "")

            if obrigatorio and not raw_value.strip():
                return {"ok": False, "mensagem": f"Informe o campo: {campo.get('ds_label', nm_campo)}."}

            params[nm_parametro_proc] = _convert_field_value(tp_campo, raw_value)

        if "P_CD_USUARIO" not in params:
            params["P_CD_USUARIO"] = usuario

        if "P_DS_MOTIVO" not in params and "motivo" in form_data:
            params["P_DS_MOTIVO"] = form_data.get("motivo") or None

        execute_named_procedure(procedure_name, params)

        return {"ok": True, "mensagem": "Processamento realizado com sucesso."}

    except ValueError:
        return {"ok": False, "mensagem": "Dados inválidos. Revise os campos informados."}

    except oracledb.DatabaseError as exc:
        error_obj = exc.args[0]
        mensagem = getattr(error_obj, "message", str(exc))
        return {"ok": False, "mensagem": mensagem}

    except Exception as exc:
        return {"ok": False, "mensagem": f"Erro inesperado: {exc}"}