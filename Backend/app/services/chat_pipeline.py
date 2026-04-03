from __future__ import annotations

import asyncio
from typing import Any

from app.agents import intelligence_agent, lingo_agent, profile_agent, response_agent
from app.agents.deps import AgentDeps
from app.core import prompts
from app.core.state_manager import AgentKVState, StateManager


async def run_chat_pipeline(
    deps: AgentDeps,
    *,
    user_id: str,
    message: str,
    traits: dict[str, Any],
    questionnaire: dict[str, Any],
    academic_load: str | None,
) -> AgentKVState:
    state = StateManager.initial(
        user_id=user_id,
        message=message,
        traits=traits,
        questionnaire=questionnaire,
        academic_load=academic_load,
        prompts_version=prompts.PROMPTS_VERSION,
    )

    profile_task = profile_agent.run(state, deps)
    intel_task = intelligence_agent.run(state, deps)
    profile_patch, intel_patch = await asyncio.gather(profile_task, intel_task)
    state = StateManager.merge(state, profile_patch)
    state = StateManager.merge(state, intel_patch)

    deps.milvus.connect()
    milvus_hits = ""
    if deps.llm.enabled:
        try:
            qvec = await deps.llm.embed(message)
            milvus_hits = deps.milvus.search_lingo(qvec)
        except Exception:  # noqa: BLE001
            milvus_hits = ""
    state = StateManager.merge(state, {"milvus_hits": milvus_hits})

    state = StateManager.merge(state, await lingo_agent.run(state, deps))
    state = StateManager.merge(state, await response_agent.run(state, deps))
    return state


def state_for_response(state: AgentKVState) -> dict[str, Any]:
    d: dict[str, Any] = state.model_dump()
    return d
