from __future__ import annotations

from typing import Any, TypedDict

from pydantic import BaseModel, Field


class AgentKVState(BaseModel):
    """Shared KV state for API responses and agent handoffs."""

    model_config = {"extra": "allow"}

    user_id: str = ""
    message: str = ""
    traits: dict[str, Any] = Field(default_factory=dict)
    questionnaire: dict[str, Any] = Field(default_factory=dict)
    academic_load: str | None = None

    profile_context: str = ""
    user_traits: str = ""

    mental_state: str = ""
    suggestions: str = ""
    follow_up: str = ""

    rag_hits: str = ""
    lingo_style: str = ""

    final_response: str = ""

    meta_prompts_version: str = ""


class AgentState(TypedDict, total=False):
    """LangGraph orchestration state."""

    user_id: str
    user_message: str
    traits: dict[str, Any]
    questionnaire: dict[str, Any]
    academic_load: str | None
    meta_prompts_version: str

    profile_context: str
    user_traits: str

    mental_state: str
    suggestions: str
    follow_up: str

    rag_hits: list[str]

    lingo_style: str
    final_response: str


class StateManager:
    @staticmethod
    def merge(state: AgentKVState, patch: dict[str, Any]) -> AgentKVState:
        data = state.model_dump()
        data.update(patch)
        return AgentKVState.model_validate(data)
