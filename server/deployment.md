# Deployment notes

## Stack

- **FastAPI** (`Backend/`) — chat and user APIs.
- **Milvus** — vector store for KGP lingo retrieval (`server/docker-compose.yml`).
- **Langflow** (optional) — run flows separately and set `LANGFLOW_BASE_URL`, `LANGFLOW_API_KEY`, and per-agent `LANGFLOW_*_FLOW_ID` variables so each agent calls `/api/v1/run/{FLOW_ID}`.

## Local compose

From `server/`:

```bash
export OPENAI_API_KEY=sk-...
docker compose up --build
```

API: `http://localhost:8000`. Health: `GET /health`. Chat: `POST /api/chat`.

## Environment variables

See `Backend/app/core/config.py` for the full list. Common entries:

- `OPENAI_API_KEY` — direct LLM + embeddings when Langflow flow IDs are not set for an agent.
- `MILVUS_URI` — default `http://localhost:19530`.
- `LANGFLOW_BASE_URL`, `LANGFLOW_API_KEY`, `LANGFLOW_PROFILE_FLOW_ID`, etc.

## Langflow flows

Design one flow per agent (or share flows) whose chat input receives the combined system + user payload built in `app/agents/bridge.py`. Point each `LANGFLOW_*_FLOW_ID` at the published flow UUID from the Langflow API pane.
