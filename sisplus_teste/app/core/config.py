from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    APP_TITLE: str = "SISPLUS"
    APP_COMPANY: str = "Unimed Sorocaba"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "troque_este_secret")
    SESSION_COOKIE: str = os.getenv("SESSION_COOKIE", "sisplus_session")
    SESSION_TTL_MIN: int = int(os.getenv("SESSION_TTL_MIN", "30"))
    SESSION_TOUCH_INTERVAL_SEC: int = int(os.getenv("SESSION_TOUCH_INTERVAL_SEC", "60"))
    SECURE_COOKIES: bool = _get_bool("SECURE_COOKIES", False)

    ORA_USER: str = os.getenv("ORA_USER", "")
    ORA_PASS: str = os.getenv("ORA_PASS", "")
    ORA_DSN: str = os.getenv("ORA_DSN", "")
    ORACLE_CLIENT: str = os.getenv("ORACLE_CLIENT", "")
    ORA_THICK: bool = _get_bool("ORA_THICK", False)


settings = Settings()
