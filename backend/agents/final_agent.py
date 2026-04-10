from __future__ import annotations

import json

from agents.bridge import invoke_model
from core import prompts
from core.deps import AgentDeps
from core.state import AgentKVState
from core.utils import get_logger, truncate_to_max_words

logger = get_logger(__name__)


def _stub_final(state: AgentKVState) -> str:
    base = (state.lingo_style or state.suggestions or state.message).strip()
    fu = (state.follow_up or "").strip()
    if fu and fu not in base:
        return f"{base}\n\n{fu}" if base else fu
    return base or fu


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.resolve_final_flow_id()
    user_block = json.dumps(
        {
            "profile_context": state.profile_context,
            "user_traits": state.user_traits,
            "mental_state": state.mental_state,
            "suggestions": state.suggestions,
            "follow_up": state.follow_up,
            "lingo_style": state.lingo_style,
        },
        ensure_ascii=False,
    )
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"final-{state.user_id}",
        system=prompts.FINAL_RESPONSE_PROMPT,
        user=user_block,
        plain_text_output=True,
    )
    cap = deps.settings.final_response_max_words

    if raw is None:
        logger.warning("Final agent: no LLM/Langflow; using stub merge")
        return {"final_response": truncate_to_max_words(_stub_final(state), cap)}
    text = raw.strip()
    if not text:
        return {"final_response": truncate_to_max_words(_stub_final(state), cap)}
    return {"final_response": truncate_to_max_words(text, cap)}
