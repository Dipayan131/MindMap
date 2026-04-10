from __future__ import annotations

import csv
from pathlib import Path

from fastapi import APIRouter, HTTPException

from database.db import get_profile, upsert_profile
from models.schemas import (
    SetTraitsIn,
    SubmitQuestionnaireIn,
    UserProfileOut,
)

router = APIRouter(tags=["user"])

_DB_DIR = Path(__file__).resolve().parent.parent / "database"


@router.post("/submit-questionnaire", response_model=UserProfileOut)
def submit_questionnaire(body: SubmitQuestionnaireIn) -> UserProfileOut:
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


@router.post("/set-traits", response_model=UserProfileOut)
def set_traits(body: SetTraitsIn) -> UserProfileOut:
    traits = dict(body.traits or {})
    if body.tone:
        traits["tone"] = body.tone
    if body.style:
        traits["style"] = body.style
    stored = get_profile(body.user_id)
    merged = upsert_profile(
        body.user_id,
        {
            "traits": traits,
            "questionnaire": dict(stored.get("questionnaire") or {}),
            "academic_load": stored.get("academic_load"),
        },
    )
    return UserProfileOut(
        user_id=body.user_id,
        questionnaire=dict(merged.get("questionnaire") or {}),
        academic_load=merged.get("academic_load"),
        traits=dict(merged.get("traits") or {}),
    )


@router.post("/user/questionnaire", response_model=UserProfileOut)
def save_questionnaire_legacy(body: SubmitQuestionnaireIn) -> UserProfileOut:
    """Compatibility: same as POST /submit-questionnaire (used by existing frontend)."""
    return submit_questionnaire(body)


@router.get("/user/{user_id}", response_model=UserProfileOut)
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


@router.get("/questionnaire")
def questionnaire_template() -> dict[str, list[dict[str, str]]]:
    """Load onboarding questions from database/questionnaire.csv."""
    path = _DB_DIR / "questionnaire.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail="questionnaire.csv not found")
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return {"questions": rows}
