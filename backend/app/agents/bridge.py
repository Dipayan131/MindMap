from __future__ import annotations

from app.agents.deps import AgentDeps
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def invoke_model(
    deps: AgentDeps,
    *,
    flow_id: str | None,
    session_id: str,
    system: str,
    user: str,
    plain_text_output: bool = False,
) -> str | None:
    """
    Langflow if base URL, API key, and flow_id are set; else OpenAI.
    Returns None if no backend is configured.
    """
    if flow_id and deps.langflow.enabled:
        combined = f"{system.strip()}\n\n---\n\n{user.strip()}"
        return await deps.langflow.run_flow(flow_id, combined, session_id)

    if not deps.llm.enabled:
        return None

    if plain_text_output:
        return await deps.llm.chat_text(system=system, user=user)
    return await deps.llm.chat_json_pref(system=system, user=user)
