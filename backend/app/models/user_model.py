from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class QuestionnaireIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    answers: dict[str, Any] = Field(default_factory=dict)
    academic_load: str | None = None
    traits: dict[str, Any] = Field(default_factory=dict)


class UserProfileOut(BaseModel):
    user_id: str
    questionnaire: dict[str, Any]
    academic_load: str | None
    traits: dict[str, Any]
