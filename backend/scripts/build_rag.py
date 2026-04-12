#!/usr/bin/env python3
"""
One-time RAG ingestion: database/questionnaire.csv + database/output.json → FAISS in rag/faiss_index/.

Run from backend:
  cd backend && python scripts/build_rag.py

Requires GEMINI_API_KEY in .env.

Optional env (reduce rate-limit bursts):
  RAG_INGEST_BATCH_SIZE=16   # docs per embedding API call
  RAG_INGEST_SLEEP_SEC=0.25  # pause between batches
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from core.config import get_settings  # noqa: E402

QUESTIONNAIRE_PATH = BACKEND_ROOT / "database" / "questionnaire.csv"
LINGO_PATH = BACKEND_ROOT / "database" / "output.json"
FAISS_DIR = BACKEND_ROOT / "rag" / "faiss_index"


def load_questionnaire() -> list[Document]:
    df = pd.read_csv(QUESTIONNAIRE_PATH)
    docs: list[Document] = []
    for _, row in df.iterrows():
        q = str(row.get("question", "")).strip()
        cat = str(row.get("category", "")).strip()
        qid = str(row.get("id", "")).strip()
        content = f"""
        Type: Questionnaire
        Question: {q}
        Category: {cat}
        """.strip()
        docs.append(
            Document(
                page_content=content,
                metadata={"type": "questionnaire", "id": qid},
            )
        )
    return docs


def load_lingo() -> list[Document]:
    if not LINGO_PATH.exists():
        raise FileNotFoundError(f"Missing lingo corpus: {LINGO_PATH}")

    data = json.loads(LINGO_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("output.json must be a JSON object mapping term → definition string")

    docs: list[Document] = []
    for term, definition in data.items():
        term = str(term).strip()
        definition = str(definition).strip() if definition is not None else ""
        if not term or not definition:
            continue
        content = f"""
IIT KGP Lingo:
Term: {term}
Meaning: {definition}
Usage: Commonly used by students in casual conversation
""".strip()
        docs.append(
            Document(
                page_content=content,
                metadata={"type": "lingo", "term": term},
            )
        )
    return docs


def _faiss_from_documents_batched(
    documents: list[Document],
    embeddings: GoogleGenerativeAIEmbeddings,
) -> FAISS:
    """Embed in smaller batches to avoid huge single requests (helps with rate limits)."""
    batch_size = max(1, int(os.environ.get("RAG_INGEST_BATCH_SIZE", "16")))
    sleep_sec = max(0.0, float(os.environ.get("RAG_INGEST_SLEEP_SEC", "0.25")))
    n = len(documents)
    if n == 0:
        raise ValueError("No documents to index")

    first = documents[:batch_size]
    print(f"Embedding batch 1 (≤{len(first)} docs)…")
    db = FAISS.from_documents(first, embeddings)

    for start in range(batch_size, n, batch_size):
        if sleep_sec:
            time.sleep(sleep_sec)
        chunk = documents[start : start + batch_size]
        bn = start // batch_size + 1
        total_b = (n + batch_size - 1) // batch_size
        print(f"Embedding batch {bn}/{total_b} ({len(chunk)} docs)…")
        db.add_documents(chunk)
    return db


def build_faiss() -> None:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise SystemExit(
            "GEMINI_API_KEY is required. Set it in the environment or backend/.env",
        )

    print("Loading questionnaire…")
    q_docs = load_questionnaire()

    print("Loading lingo…")
    lingo_docs = load_lingo()

    all_docs = q_docs + lingo_docs
    print(f"Total documents: {len(all_docs)} (questionnaire={len(q_docs)}, lingo={len(lingo_docs)})")

    kwargs: dict = {"model": settings.embedding_model}
    if settings.gemini_api_key:
        kwargs["google_api_key"] = settings.gemini_api_key
    embeddings = GoogleGenerativeAIEmbeddings(**kwargs)

    print("Building FAISS index…")
    try:
        db = _faiss_from_documents_batched(all_docs, embeddings)
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "quota" in msg:
            print("\nGoogle Gemini API rejected the request (Quota / Rate Limit).", file=sys.stderr)
            print(
                "\n  If this is a rate limit, wait a few minutes or run with:\n"
                "    RAG_INGEST_BATCH_SIZE=8 RAG_INGEST_SLEEP_SEC=1 python scripts/build_rag.py\n",
                file=sys.stderr,
            )
            raise SystemExit(1) from e
        raise e

    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Saving index to {FAISS_DIR}…")
    db.save_local(str(FAISS_DIR))

    print("RAG setup complete. Runtime loads rag/faiss_index only.")


if __name__ == "__main__":
    build_faiss()
