from __future__ import annotations

import json
from typing import Any

import httpx

from app.core.config import Settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _extract_run_message_text(payload: dict[str, Any]) -> str | None:
    outputs = payload.get("outputs") or []
    if not outputs:
        return None
    inner = (outputs[0] or {}).get("outputs") or []
    if not inner:
        return None
    results = (inner[0] or {}).get("results") or {}
    message = results.get("message") or {}
    text = message.get("text")
    return text if isinstance(text, str) else None


class LangflowService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return bool(
            self._settings.langflow_base_url
            and self._settings.langflow_api_key
        )

    async def run_flow(self, flow_id: str, input_value: str, session_id: str) -> str:
        base = (self._settings.langflow_base_url or "").rstrip("/")
        url = f"{base}/api/v1/run/{flow_id}"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self._settings.langflow_api_key or "",
        }
        body = {
            "input_value": input_value,
            "session_id": session_id,
            "input_type": "chat",
            "output_type": "chat",
            "output_component": "",
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()
        text = _extract_run_message_text(data)
        if text:
            return text
        logger.warning("Langflow response missing message text; returning raw JSON string")
        return json.dumps(data, ensure_ascii=False)
