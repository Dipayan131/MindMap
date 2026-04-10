from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

_DB_DIR = Path(__file__).resolve().parent
_USER_FILE = _DB_DIR / "user_data.json"
_lock = Lock()


def _load_raw() -> dict[str, Any]:
    if not _USER_FILE.exists():
        return {}
    try:
        return json.loads(_USER_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_raw(data: dict[str, Any]) -> None:
    _USER_FILE.parent.mkdir(parents=True, exist_ok=True)
    _USER_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_profile(user_id: str) -> dict[str, Any]:
    with _lock:
        return dict(_load_raw().get(user_id, {}))


def upsert_profile(user_id: str, data: dict[str, Any]) -> dict[str, Any]:
    with _lock:
        store = _load_raw()
        existing = dict(store.get(user_id, {}))
        existing.update(data)
        store[user_id] = existing
        _save_raw(store)
        return dict(existing)
