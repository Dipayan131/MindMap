from __future__ import annotations

import json

from agents.bridge import invoke_model
from core import prompts
from core.deps import AgentDeps
from core.state import AgentKVState
from core.utils import extract_json_object, get_logger

logger = get_logger(__name__)


def _stub(state: AgentKVState) -> dict[str, str]:
    traits = state.traits or {}
    tone = traits.get("tone") or traits.get("style") or "supportive"
    q = state.questionnaire or {}
    q_note = f" Questionnaire keys: {', '.join(sorted(q.keys())[:8])}." if q else ""
    return {
        "profile_context": (
            f"Student ({state.user_id}) — profile from traits/questionnaire only.{q_note} "
            f"Preferred tone: {tone}. (LLM offline — expand when API keys are set.)"
        ),
        "user_traits": f"{tone}, student-friendly, non-judgmental",
    }


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.langflow_profile_flow_id
    user_block = json.dumps(
        {
            "traits": state.traits,
            "questionnaire": state.questionnaire,
            "academic_load": state.academic_load,
        },
        ensure_ascii=False,
    )
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"profile-{state.user_id}",
        system=prompts.PROFILE_PROMPT,
        user=user_block,
        plain_text_output=False,
    )
    if raw is None:
        logger.warning("Profile agent: no LLM/Langflow; using stub")
        return _stub(state)
    parsed = extract_json_object(raw)
    if not parsed:
        logger.warning("Profile agent: bad JSON; using stub")
        return _stub(state)
    uc = parsed.get("user_context")
    cs = parsed.get("communication_style")
    if not isinstance(uc, str) or not isinstance(cs, str):
        return _stub(state)
    return {"profile_context": uc, "user_traits": cs}
