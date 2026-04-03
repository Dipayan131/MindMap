from __future__ import annotations

from fastapi import APIRouter, Request

from app.core import prompts
from app.models.chat_model import ChatRequest, ChatResponse
from app.services.chat_pipeline import run_chat_pipeline, state_for_response
from app.services.user_profile_store import get_profile

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat_turn(body: ChatRequest, request: Request) -> ChatResponse:
    deps = request.app.state.agent_deps
    stored = get_profile(body.user_id)
    questionnaire = dict(stored.get("questionnaire") or {})
    academic_load = stored.get("academic_load")
    traits = {**dict(stored.get("traits") or {}), **(body.traits or {})}

    state = await run_chat_pipeline(
        deps,
        user_id=body.user_id,
        message=body.message,
        traits=traits,
        questionnaire=questionnaire,
        academic_load=academic_load if isinstance(academic_load, str) else None,
    )
    return ChatResponse(
        reply=state.final_response,
        kv_state=state_for_response(state),
        prompts_version=prompts.PROMPTS_VERSION,
    )
