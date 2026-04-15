from __future__ import annotations
from dataclasses import dataclass
from app.core.Authentication import (
    get_full_name,
    get_user_roles,
    get_user_system_label,
    validate_login,
)


@dataclass
class AuthResult:
    ok: bool
    message: str = ""
    username: str = ""
    full_name: str = ""
    roles: list[int] | None = None
    app_subtitle: str = ""



def authenticate_user(username: str, password: str) -> AuthResult:
    normalized_username = (username or "").strip().upper()
    normalized_password = password or ""

    if not normalized_username or not normalized_password:
        return AuthResult(ok=False, message="Informe usuário e senha.")

    if not validate_login(normalized_username, normalized_password):
        return AuthResult(ok=False, message="Usuário ou senha inválidos.")

    return AuthResult(
        ok=True,
        username=normalized_username,
        full_name=get_full_name(normalized_username) or normalized_username,
        roles=get_user_roles(normalized_username),
        app_subtitle=get_user_system_label(normalized_username),
    )
