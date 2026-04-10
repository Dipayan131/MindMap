from __future__ import annotations

import json

from agents.bridge import invoke_model
from core import prompts
from core.deps import AgentDeps
from core.state import AgentKVState
from core.utils import extract_json_object, get_logger

logger = get_logger(__name__)


def _stub(state: AgentKVState) -> dict[str, str]:
    snippet = (state.message or "").strip()
    if len(snippet) > 280:
        snippet = snippet[:277] + "…"
    ack = (
        f"You shared: \"{snippet}\" — thanks for saying it out loud."
        if snippet
        else "Thanks for reaching out."
    )
    return {
        "mental_state": f"{ack} That kind of load is rough, especially during busy terms.",
        "suggestions": (
            "Try a 10-minute walk on campus, one small task broken into a 5-minute step, "
            "and reach out to one person you trust. If you feel unsafe, contact local emergency services."
        ),
        "follow_up": "What would help most right now — a tiny first step on the backlog, or protecting sleep tonight?",
    }


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.resolve_general_flow_id()
    user_block = json.dumps({"user_message": state.message}, ensure_ascii=False)
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"general-{state.user_id}",
        system=prompts.GENERAL_PROMPT,
        user=user_block,
        plain_text_output=False,
    )
    if raw is None:
        logger.warning("General agent: no LLM/Langflow; using stub")
        return _stub(state)
    parsed = extract_json_object(raw)
    if not parsed:
        return _stub(state)
    insight = parsed.get("insight", "")
    suggestion = parsed.get("suggestion", "")
    follow_up = parsed.get("follow_up", "")
    if not all(isinstance(x, str) for x in (insight, suggestion, follow_up)):
        return _stub(state)
    return {
        "mental_state": insight,
        "suggestions": suggestion,
        "follow_up": follow_up,
    }
