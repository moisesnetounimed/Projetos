from __future__ import annotations
import threading
import oracledb
from app.core.config import settings

_ORACLE_CLIENT_INITIALIZED = False
_ORACLE_CLIENT_LOCK = threading.Lock()


def init_oracle_client() -> None:
    global _ORACLE_CLIENT_INITIALIZED

    if _ORACLE_CLIENT_INITIALIZED:
        return

    if not settings.ORACLE_CLIENT:
        return

    with _ORACLE_CLIENT_LOCK:
        if _ORACLE_CLIENT_INITIALIZED:
            return
        try:
            oracledb.init_oracle_client(lib_dir=settings.ORACLE_CLIENT)
        except oracledb.ProgrammingError:
            # Cliente já inicializado por outro processo/thread.
            pass
        _ORACLE_CLIENT_INITIALIZED = True


def get_conn() -> oracledb.Connection:
    init_oracle_client()

    if not settings.ORA_USER or not settings.ORA_PASS or not settings.ORA_DSN:
        raise RuntimeError(
            "Oracle .env incompleto. Preencha ORA_USER, ORA_PASS e ORA_DSN."
        )

    return oracledb.connect(
        user=settings.ORA_USER,
        password=settings.ORA_PASS,
        dsn=settings.ORA_DSN,
    )
