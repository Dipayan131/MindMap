from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.deps import AgentDeps
from core.langflow_service import LangflowService
from core.llm_service import LLMService
from langgraph_flow import compile_chat_graph
from rag.retriever import warm_vectorstore
from routes import chat, user


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    llm = LLMService(settings)
    langflow = LangflowService(settings)
    deps = AgentDeps(settings=settings, llm=llm, langflow=langflow)
    warm_vectorstore(settings)
    deps.chat_graph = compile_chat_graph(deps)
    app.state.agent_deps = deps
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(chat.router, prefix="/api")
    application.include_router(user.router, prefix="/api")
    return application


app = create_app()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
