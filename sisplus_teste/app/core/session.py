from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from itsdangerous import BadSignature, URLSafeSerializer
from app.core.config import settings

_serializer = URLSafeSerializer(settings.SESSION_SECRET, salt="app_sisplus_session")



def utcnow() -> datetime:
    return datetime.now(timezone.utc)



def _serialize_dt(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()



def _parse_dt(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None



def build_session_payload(*, user: str, full_name: str, roles: list[int], app_subtitle: str = "") -> Dict[str, Any]:
    now = utcnow()
    return {
        "user": user,
        "full_name": full_name,
        "roles": roles,
        "app_subtitle": app_subtitle,
        "created_at": _serialize_dt(now),
        "last_activity": _serialize_dt(now),
    }



def encode_session(data: Dict[str, Any]) -> str:
    return _serializer.dumps(data)



def decode_session(token: str) -> Optional[Dict[str, Any]]:
    if not token or token.strip().lower() in {"null", "none", "undefined"}:
        return None
    try:
        payload = _serializer.loads(token)
    except BadSignature:
        return None
    return payload if isinstance(payload, dict) else None



def is_session_expired(payload: Dict[str, Any]) -> bool:
    last_activity = _parse_dt(payload.get("last_activity"))
    if last_activity is None:
        return True
    return utcnow() - last_activity > timedelta(minutes=settings.SESSION_TTL_MIN)



def should_touch_session(payload: Dict[str, Any]) -> bool:
    last_activity = _parse_dt(payload.get("last_activity"))
    if last_activity is None:
        return True
    return utcnow() - last_activity >= timedelta(seconds=settings.SESSION_TOUCH_INTERVAL_SEC)



def touch_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    updated = dict(payload)
    updated["last_activity"] = _serialize_dt(utcnow())
    return updated
