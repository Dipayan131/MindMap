from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.agents.deps import AgentDeps
from app.api import chat, user
from app.core.config import get_settings
from app.services.langflow_service import LangflowService
from app.services.llm_service import LLMService
from app.services.milvus_service import MilvusService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    milvus = MilvusService(settings)
    milvus.connect()
    llm = LLMService(settings)
    langflow = LangflowService(settings)
    if llm.enabled and milvus.collection_created_this_boot:
        await milvus.seed_default_corpus(llm.embed)
    app.state.agent_deps = AgentDeps(
        settings=settings,
        llm=llm,
        langflow=langflow,
        milvus=milvus,
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    app.include_router(chat.router, prefix="/api")
    app.include_router(user.router, prefix="/api")
    return app


app = create_app()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
