from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "MindMap Mental Health API"
    debug: bool = False

    # Direct LLM (fallback when Langflow flow IDs are not set)
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Langflow — POST {langflow_base_url}/api/v1/run/{flow_id}
    langflow_base_url: str | None = None
    langflow_api_key: str | None = None
    langflow_profile_flow_id: str | None = None
    langflow_intelligence_flow_id: str | None = None
    langflow_lingo_flow_id: str | None = None
    langflow_response_flow_id: str | None = None

    # Milvus
    milvus_uri: str = "http://localhost:19530"
    milvus_token: str | None = None
    milvus_collection_kgp: str = "kgp_lingo"
    milvus_top_k: int = 5
    milvus_connect_timeout: float = 5.0

    # CORS — comma-separated origins (Next.js dev: http://localhost:3000)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
