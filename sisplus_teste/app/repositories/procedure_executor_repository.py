from __future__ import annotations
from typing import Any
from app.core.db import get_conn


def execute_named_procedure(procedure_name: str, params: dict[str, Any]) -> None:
    placeholders = []
    bind_values: dict[str, Any] = {}

    for key, value in params.items():
        placeholders.append(f"{key} => :{key}")
        bind_values[key] = value

    sql = f"BEGIN {procedure_name}({', '.join(placeholders)}); END;"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, bind_values)