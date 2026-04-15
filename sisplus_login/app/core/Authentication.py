from __future__ import annotations
import re
from typing import Any
from app.core.db import get_conn

def _parse_roles(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        roles: list[int] = []
        for item in value:
            roles.extend(_parse_roles(item))
        return sorted(set(roles))

    text = str(value).strip()
    if not text:
        return []

    numbers = re.findall(r"\d+", text)
    return sorted({int(number) for number in numbers})



def validate_login(username: str, password: str) -> bool:
    with get_conn() as conn:
        cur = conn.cursor()
        result = cur.callfunc(
            "CUSTOM.PKG_SISPLUS.FNC_VALIDA_USUARIO_LOGIN",
            int,
            [username, password],
        )
    return int(result) == 1



def get_user_roles(username: str) -> list[int]:
    with get_conn() as conn:
        cur = conn.cursor()
        roles = cur.callfunc("CUSTOM.PKG_SISPLUS.FNC_VE_ROLES", str, [username])
    return _parse_roles(roles)



def get_full_name(username: str) -> str:
    with get_conn() as conn:
        cur = conn.cursor()
        full_name = cur.callfunc("CUSTOM.PKG_SISPLUS.FNC_EXIBE_NOME", str, [username])
    return str(full_name or "").strip()



def get_user_system_label(username: str) -> str:
    with get_conn() as conn:
        cur = conn.cursor()
        label = cur.callfunc("CUSTOM.PKG_SISPLUS.FNC_EXIBE_SISTEMA", str, [username])
    return str(label or "SISPLUS").strip() or "SISPLUS"


def get_url_sistema(url: str) -> str:
    with get_conn() as conn:
        cur = conn.cursor()
        url = cur.callfunc("CUSTOM.PKG_SISPLUS.FNC_URL_SISTEMA",str,[url])
        return url
