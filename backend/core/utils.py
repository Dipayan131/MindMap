from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def truncate_to_max_words(text: str, max_words: int) -> str:
    """Trim to at most max_words whitespace-separated tokens; append … if trimmed."""
    if max_words <= 0:
        return ""
    s = (text or "").strip()
    if not s:
        return ""
    parts = s.split()
    if len(parts) <= max_words:
        return s
    return " ".join(parts[:max_words]) + "…"


def extract_json_object(text: str) -> dict[str, Any] | None:
    """Best-effort parse of a JSON object from model output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            obj = json.loads(m.group())
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None
    return None
