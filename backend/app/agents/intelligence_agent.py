from __future__ import annotations

import json

from app.agents.bridge import invoke_model
from app.agents.deps import AgentDeps
from app.core import prompts
from app.core.state_manager import AgentKVState
from app.utils.helpers import extract_json_object
from app.utils.logger import get_logger

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
        "insight": f"{ack} That kind of load is rough, especially during busy terms.",
        "suggestion": (
            "Try a 10-minute walk on campus, one small task broken into a 5-minute step, "
            "and reach out to one person you trust. If you feel unsafe, contact local emergency services."
        ),
        "follow_up": "What would help most right now — a tiny first step on the backlog, or protecting sleep tonight?",
    }


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.langflow_intelligence_flow_id
    q_summary = json.dumps(state.questionnaire, ensure_ascii=False) if state.questionnaire else "{}"
    user_block = json.dumps(
        {
            "user_message": state.message,
            "traits": state.traits,
            "questionnaire_summary": q_summary,
        },
        ensure_ascii=False,
    )
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"intel-{state.user_id}",
        system=prompts.INTELLIGENCE_PROMPT,
        user=user_block,
        plain_text_output=False,
    )
    if raw is None:
        logger.warning("Intelligence agent: no LLM/Langflow; using stub")
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
        "insight": insight,
        "suggestion": suggestion,
        "follow_up": follow_up,
    }
