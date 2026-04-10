from __future__ import annotations

from openai import AsyncOpenAI

from core.config import Settings
from core.utils import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncOpenAI | None = None
        if settings.openai_api_key:
            kwargs: dict = {"api_key": settings.openai_api_key}
            if settings.openai_base_url:
                kwargs["base_url"] = settings.openai_base_url
            self._client = AsyncOpenAI(**kwargs)

    @property
    def enabled(self) -> bool:
        return self._client is not None

    async def chat_json_pref(self, *, system: str, user: str) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client not configured (OPENAI_API_KEY missing)")
        resp = await self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
        )
        choice = resp.choices[0].message.content
        if not choice:
            raise RuntimeError("Empty LLM response")
        return choice

    async def chat_text(self, *, system: str, user: str) -> str:
        if not self._client:
            raise RuntimeError("OpenAI client not configured (OPENAI_API_KEY missing)")
        resp = await self._client.chat.completions.create(
            model=self._settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.5,
        )
        choice = resp.choices[0].message.content
        if not choice:
            raise RuntimeError("Empty LLM response")
        return choice

    async def embed(self, text: str) -> list[float]:
        if not self._client:
            raise RuntimeError("OpenAI client not configured (OPENAI_API_KEY missing)")
        clean = (text or "").replace("\n", " ")[:8000]
        resp = await self._client.embeddings.create(
            model=self._settings.embedding_model,
            input=clean,
        )
        return list(resp.data[0].embedding)
