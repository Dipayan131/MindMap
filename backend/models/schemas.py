from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    traits: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    reply: str
    kv_state: dict[str, Any]
    prompts_version: str


class SubmitQuestionnaireIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    answers: dict[str, Any] = Field(default_factory=dict)
    academic_load: str | None = None
    traits: dict[str, Any] = Field(default_factory=dict)


class SetTraitsIn(BaseModel):
    user_id: str = Field(..., min_length=1)
    tone: str | None = None
    style: str | None = None
    traits: dict[str, Any] = Field(default_factory=dict)


class UserProfileOut(BaseModel):
    user_id: str
    questionnaire: dict[str, Any]
    academic_load: str | None
    traits: dict[str, Any]
