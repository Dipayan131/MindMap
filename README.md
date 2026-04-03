# MindMap — Mental health chatbot (IIT KGP)

Monorepo layout (same idea as `main`):

- **`frontend/`** — Next.js app (from `main`).
- **`backend/`** — FastAPI multi-agent API, Milvus + optional Langflow, plus **`backend/server/`** (Docker Compose, nginx example, deployment notes).
- **`docs/`** — backend architecture notes.

## Frontend

```bash
cd frontend
cp .env.example .env.local   # optional; defaults to http://127.0.0.1:8000
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The UI calls the FastAPI backend (`POST /api/chat`, `POST /api/user/questionnaire`). Start the backend on port **8000** first, or set `NEXT_PUBLIC_API_URL` in `.env.local`.

**CORS:** backend allows `http://localhost:3000` and `http://127.0.0.1:3000` by default. Override with `CORS_ORIGINS` in the backend `.env` (comma-separated).

See `frontend/README.md` for details.

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # optional; stubs used if unset
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `POST /api/user/questionnaire` — save traits + questionnaire.
- `POST /api/chat` — `{ "user_id", "message", "traits"? }` → `reply` + full `kv_state`.

**Milvus (optional):** from `backend/server/`, run `docker compose up --build`, or set `MILVUS_URI` to a running instance.

See `backend/server/deployment.md` for Langflow and production notes.
