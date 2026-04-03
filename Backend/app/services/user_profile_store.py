from __future__ import annotations

from threading import Lock
from typing import Any

_lock = Lock()
_profiles: dict[str, dict[str, Any]] = {}


def get_profile(user_id: str) -> dict[str, Any]:
    with _lock:
        return dict(_profiles.get(user_id, {}))


def upsert_profile(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        existing = dict(_profiles.get(user_id, {}))
        existing.update(data)
        _profiles[user_id] = existing
        return dict(existing)
