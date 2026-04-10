from __future__ import annotations

from typing import Any

from core import prompts
from core.deps import AgentDeps
from core.state import AgentKVState, AgentState


def _result_to_kv(
    *,
    user_id: str,
    message: str,
    traits: dict[str, Any],
    questionnaire: dict[str, Any],
    academic_load: str | None,
    prompts_version: str,
    result: dict[str, Any],
) -> AgentKVState:
    hits = result.get("rag_hits")
    rag_str = "\n".join(hits) if isinstance(hits, list) else str(result.get("rag_hits") or "")
    return AgentKVState(
        user_id=user_id,
        message=message,
        traits=traits,
        questionnaire=questionnaire,
        academic_load=academic_load,
        meta_prompts_version=prompts_version,
        profile_context=str(result.get("profile_context") or ""),
        user_traits=str(result.get("user_traits") or ""),
        mental_state=str(result.get("mental_state") or ""),
        suggestions=str(result.get("suggestions") or ""),
        follow_up=str(result.get("follow_up") or ""),
        rag_hits=rag_str,
        lingo_style=str(result.get("lingo_style") or ""),
        final_response=str(result.get("final_response") or ""),
    )


async def run_chat_pipeline(
    deps: AgentDeps,
    *,
    user_id: str,
    message: str,
    traits: dict[str, Any],
    questionnaire: dict[str, Any],
    academic_load: str | None,
) -> AgentKVState:
    graph = deps.chat_graph
    if graph is None:
        raise RuntimeError("chat_graph not compiled")

    init: AgentState = {
        "user_id": user_id,
        "user_message": message,
        "traits": traits,
        "questionnaire": questionnaire,
        "academic_load": academic_load,
        "meta_prompts_version": prompts.PROMPTS_VERSION,
    }
    raw = await graph.ainvoke(init)
    return _result_to_kv(
        user_id=user_id,
        message=message,
        traits=traits,
        questionnaire=questionnaire,
        academic_load=academic_load,
        prompts_version=prompts.PROMPTS_VERSION,
        result=raw,
    )


def state_for_response(state: AgentKVState) -> dict[str, Any]:
    return state.model_dump()
