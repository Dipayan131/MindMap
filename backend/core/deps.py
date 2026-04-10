from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.config import Settings
from core.langflow_service import LangflowService
from core.llm_service import LLMService


@dataclass
class AgentDeps:
    settings: Settings
    llm: LLMService
    langflow: LangflowService
    chat_graph: Any | None = None
