from __future__ import annotations

import json

from agents.bridge import invoke_model
from core import prompts
from core.deps import AgentDeps
from core.state import AgentKVState
from core.utils import extract_json_object, get_logger

logger = get_logger(__name__)


def _draft_from_state(state: AgentKVState) -> str:
    parts = [state.mental_state, state.suggestions]
    return "\n\n".join(p for p in parts if p)


async def run(state: AgentKVState, deps: AgentDeps) -> dict[str, str]:
    draft = _draft_from_state(state)
    if not draft.strip():
        draft = state.message

    rag_blob = state.rag_hits or "(no RAG hits — add corpus under rag/data/)"
    user_block = json.dumps(
        {
            "draft_reply": draft,
            "optional_follow_up": state.follow_up or "",
            "rag_hits": rag_blob,
            "traits": state.traits,
        },
        ensure_ascii=False,
    )
    flow_id = deps.settings.langflow_lingo_flow_id
    raw = await invoke_model(
        deps,
        flow_id=flow_id,
        session_id=f"lingo-{state.user_id}",
        system=prompts.LINGO_PROMPT,
        user=user_block,
        plain_text_output=False,
    )
    if raw is None:
        logger.warning("Lingo agent: no LLM/Langflow; passing draft through")
        return {"lingo_style": draft}
    parsed = extract_json_object(raw)
    if not parsed:
        return {"lingo_style": draft}
    style = parsed.get("lingo_style")
    if not isinstance(style, str) or not style.strip():
        return {"lingo_style": draft}
    return {"lingo_style": style}
