from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentKVState(BaseModel):
    """
    Shared KV state passed through the pipeline. Agents read the full model and
    return partial updates (dict) merged by StateManager.
    """

    model_config = {"extra": "allow"}

    user_id: str = ""
    message: str = ""
    traits: dict[str, Any] = Field(default_factory=dict)
    questionnaire: dict[str, Any] = Field(default_factory=dict)
    academic_load: str | None = None

    user_context: str = ""
    communication_style: str = ""

    insight: str = ""
    suggestion: str = ""
    follow_up: str = ""

    milvus_hits: str = ""
    lingo_style: str = ""

    final_response: str = ""

    meta_prompts_version: str = ""


class StateManager:
    """Merges agent outputs into immutable-ish snapshots for tracing."""

    @staticmethod
    def initial(
        *,
        user_id: str,
        message: str,
        traits: dict[str, Any],
        questionnaire: dict[str, Any],
        academic_load: str | None,
        prompts_version: str,
    ) -> AgentKVState:
        return AgentKVState(
            user_id=user_id,
            message=message,
            traits=traits,
            questionnaire=questionnaire,
            academic_load=academic_load,
            meta_prompts_version=prompts_version,
        )

    @staticmethod
    def merge(state: AgentKVState, patch: dict[str, Any]) -> AgentKVState:
        data = state.model_dump()
        data.update(patch)
        return AgentKVState.model_validate(data)

    @staticmethod
    def to_kv_dict(state: AgentKVState) -> dict[str, Any]:
        return state.model_dump()
