# MindMap — Mental health chatbot (IIT KGP)

Monorepo layout:

- `Backend/` — FastAPI app, multi-agent pipeline, Milvus + optional Langflow, and **`Backend/server/`** (Docker Compose, nginx example, deployment notes).
- `docs/` — architecture notes.

## Quick start (backend only)

```bash
cd Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # optional; stubs used if unset
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `POST /api/user/questionnaire` — save traits + questionnaire.
- `POST /api/chat` — `{ "user_id", "message", "traits"? }` → `reply` + full `kv_state`.

With Milvus: from `Backend/server/`, run `docker compose up --build` (see `Backend/server/docker-compose.yml`), or point `MILVUS_URI` at a running instance.

See `Backend/server/deployment.md` for Langflow and production notes.
