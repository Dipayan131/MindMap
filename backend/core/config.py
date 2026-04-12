from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MindMap Mental Health API"
    debug: bool = False

    gemini_api_key: str | None = None
    llm_model: str = "gemini-2.5-flash"
    embedding_model: str = "text-embedding-004"

    langflow_base_url: str | None = None
    langflow_api_key: str | None = None
    langflow_profile_flow_id: str | None = None
    langflow_general_flow_id: str | None = None
    langflow_intelligence_flow_id: str | None = None  # alias for langflow_general_flow_id
    langflow_lingo_flow_id: str | None = None
    langflow_final_flow_id: str | None = None
    langflow_response_flow_id: str | None = None  # alias for langflow_final_flow_id

    # LangChain FAISS index (built by scripts/build_rag.py; relative to backend root)
    langchain_faiss_dir: str = "rag/faiss_index"
    rag_similarity_fetch_k: int = 20
    rag_top_k: int = 5

    # Hard cap on words in the user-visible reply (LLM is instructed; this truncates if needed)
    final_response_max_words: int = 40

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    def resolve_path(self, relative: str) -> Path:
        return (BACKEND_ROOT / relative).resolve()

    def resolve_general_flow_id(self) -> str | None:
        return self.langflow_general_flow_id or self.langflow_intelligence_flow_id

    def resolve_final_flow_id(self) -> str | None:
        return self.langflow_final_flow_id or self.langflow_response_flow_id


@lru_cache
def get_settings() -> Settings:
    return Settings()
