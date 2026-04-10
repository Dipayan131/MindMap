from __future__ import annotations

from fastapi import APIRouter, Request

from core import prompts
from core.pipeline import run_chat_pipeline, state_for_response
from database.db import get_profile
from models.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
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
