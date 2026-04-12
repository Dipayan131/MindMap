from __future__ import annotations

import asyncio

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.config import Settings, get_settings
from core.utils import get_logger

logger = get_logger(__name__)

_vectorstore: FAISS | None = None
_vectorstore_loaded: bool = False


def _embeddings_from_settings(settings: Settings) -> GoogleGenerativeAIEmbeddings:
    kwargs: dict = {"model": settings.embedding_model}
    if settings.gemini_api_key:
        kwargs["google_api_key"] = settings.gemini_api_key
    return GoogleGenerativeAIEmbeddings(**kwargs)


def load_vectorstore(settings: Settings | None = None) -> FAISS | None:
    """
    Load LangChain FAISS index from rag/faiss_index (built by scripts/build_rag.py).
    Returns None if index is missing or load fails.
    """
    global _vectorstore, _vectorstore_loaded
    if _vectorstore_loaded:
        return _vectorstore

    settings = settings or get_settings()
    path = settings.resolve_path(settings.langchain_faiss_dir)
    index_faiss = path / "index.faiss"
    if not index_faiss.exists():
        logger.warning(
            "FAISS index not found at %s — run: cd backend && python scripts/build_rag.py",
            path,
        )
        _vectorstore = None
        _vectorstore_loaded = True
        return None

    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY missing; cannot load embeddings for RAG retrieval")
        _vectorstore = None
        _vectorstore_loaded = True
        return None

    try:
        embeddings = _embeddings_from_settings(settings)
        db = FAISS.load_local(
            str(path),
            embeddings,
            allow_dangerous_deserialization=True,
        )
        _vectorstore = db
        _vectorstore_loaded = True
        logger.info("Loaded LangChain FAISS index from %s", path)
        return db
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to load FAISS index: %s", exc)
        _vectorstore = None
        _vectorstore_loaded = True
        return None


def clear_vectorstore_cache() -> None:
    """Test / reload hook."""
    global _vectorstore, _vectorstore_loaded
    _vectorstore = None
    _vectorstore_loaded = False


def retrieve_by_type(
    query: str,
    doc_type: str,
    *,
    k: int = 5,
    fetch_k: int = 20,
    settings: Settings | None = None,
) -> list[Document]:
    """
    Similarity search then filter by metadata['type'].
    doc_type: 'questionnaire' | 'lingo'
    """
    q = (query or "").strip()
    if not q:
        return []

    db = load_vectorstore(settings)
    if db is None:
        return []

    try:
        docs = db.similarity_search(q, k=fetch_k)
    except Exception as exc:  # noqa: BLE001
        logger.warning("similarity_search failed: %s", exc)
        return []

    filtered: list[Document] = [
        doc for doc in docs if (doc.metadata or {}).get("type") == doc_type
    ]
    return filtered[:k]


async def retrieve_by_type_async(
    query: str,
    doc_type: str,
    *,
    k: int = 5,
    fetch_k: int = 20,
    settings: Settings | None = None,
) -> list[Document]:
    return await asyncio.to_thread(
        retrieve_by_type,
        query,
        doc_type,
        k=k,
        fetch_k=fetch_k,
        settings=settings,
    )


def warm_vectorstore(settings: Settings | None = None) -> None:
    load_vectorstore(settings)
