from __future__ import annotations

from dataclasses import dataclass

from app.core.config import Settings
from app.services.langflow_service import LangflowService
from app.services.llm_service import LLMService
from app.services.milvus_service import MilvusService


@dataclass
class AgentDeps:
    settings: Settings
    llm: LLMService
    langflow: LangflowService
    milvus: MilvusService
