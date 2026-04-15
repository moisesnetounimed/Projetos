from __future__ import annotations
import uuid
from decimal import Decimal, InvalidOperation
import oracledb
from app.core.db import get_conn
from app.repositories.financeiro.financeiro_rateio_staging_repository import (
    limpar_lote_rateio,
    inserir_itens_rateio,
)


def gerar_id_lote() -> str:
    return uuid.uuid4().hex[:30]


def _to_int(valor: str, campo: str) -> int:
    if not valor or not str(valor).strip():
        raise ValueError(f"Informe o campo {campo}.")
    return int(str(valor).strip())


def _to_decimal(valor: str, campo: str) -> float:
    if not valor or not str(valor).strip():
        raise ValueError(f"Informe o campo {campo}.")
    try:
        texto = str(valor).strip().replace(".", "").replace(",", ".")
        return float(Decimal(texto))
    except InvalidOperation:
        raise ValueError(f"Valor inválido para {campo}.")


def normalizar_itens_rateio(itens: list[dict]) -> list[dict]:
    if not itens:
        raise ValueError("Informe ao menos uma linha de rateio.")

    itens_normalizados: list[dict] = []

    for idx, item in enumerate(itens, start=1):
        cd_setor = _to_int(item.get("cd_setor", ""), f"Setor da linha {idx}")
        cd_item_res = _to_int(item.get("cd_item_res", ""), f"Conta Custo da linha {idx}")
        cd_reduzido = _to_int(item.get("cd_reduzido", ""), f"Conta Contábil da linha {idx}")
        vl_rateio = _to_decimal(item.get("vl_rateio", ""), f"Valor Rateio da linha {idx}")
        dt_competencia = str(item.get("dt_competencia", "")).strip()

        if not dt_competencia:
            raise ValueError(f"Informe a competência da linha {idx}.")

        itens_normalizados.append(
            {
                "cd_setor": cd_setor,
                "cd_item_res": cd_item_res,
                "cd_reduzido": cd_reduzido,
                "vl_rateio": vl_rateio,
                "dt_competencia": dt_competencia,
            }
        )

    return itens_normalizados


def salvar_e_processar_rateio(
    cd_con_pag: str,
    motivo: str,
    usuario: str,
    itens: list[dict],
) -> dict[str, str | bool]:
    try:
        cd_con_pag_int = int(str(cd_con_pag).strip())
        itens_normalizados = normalizar_itens_rateio(itens)

        id_lote = gerar_id_lote()
        limpar_lote_rateio(id_lote)
        inserir_itens_rateio(
            id_lote=id_lote,
            cd_con_pag=cd_con_pag_int,
            usuario=usuario,
            itens=itens_normalizados,
        )

        with get_conn() as conn:
            cur = conn.cursor()
            cur.callproc(
                "CUSTOM.PKG_APP_FINANCEIRO.PRC_ALTERA_RATEIO_CONPAG",
                [
                    id_lote,
                    cd_con_pag_int,
                    usuario,
                    motivo or None,
                ],
            )

        return {"ok": True, "mensagem": "Rateio alterado com sucesso."}

    except ValueError as exc:
        return {"ok": False, "mensagem": str(exc)}

    except oracledb.DatabaseError as exc:
        error_obj = exc.args[0]
        mensagem = getattr(error_obj, "message", str(exc))
        return {"ok": False, "mensagem": mensagem}

    except Exception as exc:
        return {"ok": False, "mensagem": f"Erro inesperado: {exc}"}