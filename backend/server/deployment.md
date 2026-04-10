# Deployment notes

## Stack

- **FastAPI** (`backend/app.py`, `routes/`) — chat and user APIs.
- **FAISS (LangChain)** — index under `rag/faiss_index/` built by `python scripts/build_rag.py` from `database/questionnaire.csv` and `database/output.json` (runtime loads only the index).
- **Langflow** (optional) — run flows separately and set `LANGFLOW_BASE_URL`, `LANGFLOW_API_KEY`, and per-agent `LANGFLOW_*_FLOW_ID` variables so each agent calls `/api/v1/run/{FLOW_ID}`.

## Run the API locally

From `backend/`:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # optional; stubs used if unset
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API: `http://localhost:8000`. Health: `GET /health`. Chat: `POST /api/chat`.

**RAG index (one-time):** with `OPENAI_API_KEY` set, from `backend/` run `python scripts/build_rag.py` to embed `database/questionnaire.csv` + `database/output.json` into `rag/faiss_index/`.

Optional: `nginx.conf` in this folder is an example reverse proxy in front of Uvicorn (TLS / production); configure it on your host if you use nginx.

## Environment variables

See `backend/core/config.py` for the full list. Common entries:

- `OPENAI_API_KEY` — direct LLM + embeddings when Langflow flow IDs are not set for an agent.
- `CORS_ORIGINS` — comma-separated list for the Next.js app (default includes `http://localhost:3000`).
- `LANGFLOW_BASE_URL`, `LANGFLOW_API_KEY`, `LANGFLOW_PROFILE_FLOW_ID`, `LANGFLOW_GENERAL_FLOW_ID` (or `LANGFLOW_INTELLIGENCE_FLOW_ID`), etc.

## Langflow flows

Design one flow per agent (or share flows) whose chat input receives the combined system + user payload built in `backend/agents/bridge.py`. Point each `LANGFLOW_*_FLOW_ID` at the published flow UUID from the Langflow API pane.
