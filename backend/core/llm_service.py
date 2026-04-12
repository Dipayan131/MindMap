from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from core.config import Settings
from core.utils import get_logger

logger = get_logger(__name__)


class LLMService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._chat_json: ChatGoogleGenerativeAI | None = None
        self._chat_text: ChatGoogleGenerativeAI | None = None
        self._embeddings: GoogleGenerativeAIEmbeddings | None = None
        if settings.gemini_api_key:
            self._chat_json = ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.gemini_api_key,
                temperature=0.4,
            )
            self._chat_text = ChatGoogleGenerativeAI(
                model=settings.llm_model,
                google_api_key=settings.gemini_api_key,
                temperature=0.5,
            )
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=settings.embedding_model,
                google_api_key=settings.gemini_api_key,
            )

    @property
    def enabled(self) -> bool:
        return self._chat_json is not None

    async def chat_json_pref(self, *, system: str, user: str) -> str:
        if not self._chat_json:
            raise RuntimeError("Gemini client not configured (GEMINI_API_KEY missing)")
        resp = await self._chat_json.ainvoke([("system", system), ("human", user)])
        choice = resp.content
        if not choice:
            raise RuntimeError("Empty LLM response")
        return choice if isinstance(choice, str) else str(choice[0])

    async def chat_text(self, *, system: str, user: str) -> str:
        if not self._chat_text:
            raise RuntimeError("Gemini client not configured (GEMINI_API_KEY missing)")
        resp = await self._chat_text.ainvoke([("system", system), ("human", user)])
        choice = resp.content
        if not choice:
            raise RuntimeError("Empty LLM response")
        return choice if isinstance(choice, str) else str(choice[0])

    async def embed(self, text: str) -> list[float]:
        if not self._embeddings:
            raise RuntimeError("Gemini client not configured (GEMINI_API_KEY missing)")
        clean = (text or "").replace("\n", " ")[:8000]
        return await self._embeddings.aembed_query(clean)
