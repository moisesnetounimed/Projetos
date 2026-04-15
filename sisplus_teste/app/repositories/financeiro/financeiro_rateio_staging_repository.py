from __future__ import annotations
from typing import Iterable
from app.core.db import get_conn


def limpar_lote_rateio(id_lote: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM CUSTOM.APP_FIN_RATEIO_ITEM WHERE ID_LOTE = :id_lote",
            {"id_lote": id_lote},
        )
        conn.commit()


def inserir_itens_rateio(
    id_lote: str,
    cd_con_pag: int,
    usuario: str,
    itens: Iterable[dict],
) -> None:
    with get_conn() as conn:
        cur = conn.cursor()

        nr_linha = 1
        for item in itens:
            cur.execute(
                """
                INSERT INTO CUSTOM.APP_FIN_RATEIO_ITEM (
                    CD_RATEIO_ITEM,
                    ID_LOTE,
                    CD_CON_PAG,
                    NR_LINHA,
                    CD_SETOR,
                    CD_ITEM_RES,
                    CD_REDUZIDO,
                    VL_RATEIO,
                    DT_COMPETENCIA,
                    CD_USUARIO_INC,
                    DT_INCLUSAO
                ) VALUES (
                    CUSTOM.SEQ_APP_FIN_RATEIO_ITEM.NEXTVAL,
                    :id_lote,
                    :cd_con_pag,
                    :nr_linha,
                    :cd_setor,
                    :cd_item_res,
                    :cd_reduzido,
                    :vl_rateio,
                    TO_DATE(:dt_competencia, 'YYYY-MM-DD'),
                    :usuario,
                    SYSDATE
                )
                """,
                {
                    "id_lote": id_lote,
                    "cd_con_pag": cd_con_pag,
                    "nr_linha": nr_linha,
                    "cd_setor": int(item["cd_setor"]),
                    "cd_item_res": int(item["cd_item_res"]),
                    "cd_reduzido": int(item["cd_reduzido"]),
                    "vl_rateio": float(item["vl_rateio"]),
                    "dt_competencia": item["dt_competencia"],
                    "usuario": usuario,
                },
            )
            nr_linha += 1

        conn.commit()