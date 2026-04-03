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
    traits = state.traits or {}
    tone = traits.get("tone") or traits.get("style") or "supportive"
    return {
        "user_context": (
            f"Student ({state.user_id}) wrote about their experience. "
            f"Preferred tone: {tone}. (LLM offline — expand when API keys are set.)"
        ),
        "communication_style": f"{tone}, student-friendly, non-judgmental",
    }


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    flow_id = deps.settings.langflow_profile_flow_id
    user_block = json.dumps(
        {
            "user_message": state.message,
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
    return {"user_context": uc, "communication_style": cs}
