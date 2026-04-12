from __future__ import annotations

from core.deps import AgentDeps
from core.utils import get_logger

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
    if flow_id and deps.langflow.enabled:
        try:
            combined = f"{system.strip()}\n\n---\n\n{user.strip()}"
            return await deps.langflow.run_flow(flow_id, combined, session_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Langflow request failed (%s): %s", type(exc).__name__, exc)
            return None

    if not deps.llm.enabled:
        return None

    try:
        if plain_text_output:
            return await deps.llm.chat_text(system=system, user=user)
        return await deps.llm.chat_json_pref(system=system, user=user)
    except Exception as exc:
        logger.warning(
            "Gemini unavailable (%s): %s — using agent stub/fallback",
            type(exc).__name__,
            exc,
        )
        return None
