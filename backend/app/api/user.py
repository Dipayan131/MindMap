from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.user_model import QuestionnaireIn, UserProfileOut
from app.services.user_profile_store import get_profile, upsert_profile

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/questionnaire", response_model=UserProfileOut)
def save_questionnaire(body: QuestionnaireIn) -> UserProfileOut:
    merged = upsert_profile(
        body.user_id,
        {
            "questionnaire": body.answers,
            "academic_load": body.academic_load,
            "traits": body.traits,
        },
    )
    return UserProfileOut(
        user_id=body.user_id,
        questionnaire=dict(merged.get("questionnaire") or {}),
        academic_load=merged.get("academic_load"),
        traits=dict(merged.get("traits") or {}),
    )


@router.get("/{user_id}", response_model=UserProfileOut)
def read_profile(user_id: str) -> UserProfileOut:
    data = get_profile(user_id)
    if not data:
        raise HTTPException(status_code=404, detail="User profile not found")
    return UserProfileOut(
        user_id=user_id,
        questionnaire=dict(data.get("questionnaire") or {}),
        academic_load=data.get("academic_load"),
        traits=dict(data.get("traits") or {}),
    )
