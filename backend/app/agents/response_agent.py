from __future__ import annotations

import json

from app.agents.bridge import invoke_model
from app.agents.deps import AgentDeps
from app.core import prompts
from app.core.state_manager import AgentKVState
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _stub_final(state: AgentKVState) -> str:
    base = (state.lingo_style or state.suggestion or state.message).strip()
    fu = (state.follow_up or "").strip()
    # Lingo stub passes draft that already embeds "Follow-up to ask: …" — avoid asking twice.
    if fu and fu not in base:
        return f"{base}\n\n{fu}" if base else fu
    return base or fu


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.langflow_response_flow_id
    user_block = json.dumps(
        {
            "user_context": state.user_context,
            "communication_style": state.communication_style,
            "insight": state.insight,
            "suggestion": state.suggestion,
            "follow_up": state.follow_up,
            "lingo_style": state.lingo_style,
        },
        ensure_ascii=False,
    )
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"reply-{state.user_id}",
        system=prompts.FINAL_RESPONSE_PROMPT,
        user=user_block,
        plain_text_output=True,
    )
    if raw is None:
        logger.warning("Response agent: no LLM/Langflow; using stub merge")
        return {"final_response": _stub_final(state)}
    text = raw.strip()
    if not text:
        return {"final_response": _stub_final(state)}
    return {"final_response": text}
