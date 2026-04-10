# MindMap — Mental health chatbot (IIT KGP)

Monorepo layout:

- **`frontend/`** — Next.js app (port **3000**): Firebase auth (`/login`, `/register`), chat UI, FastAPI integration.
- **`backend/`** — FastAPI multi-agent API (FAISS RAG, optional Langflow), plus **`backend/server/`** (optional nginx example, deployment notes).

## Frontend

```bash
cd frontend
cp .env.example .env.local   # set BACKEND_URL (default 127.0.0.1:8000) + Firebase vars
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Configure Firebase for sign-in. The UI loads **`GET /api/questionnaire`**, saves **`POST /api/submit-questionnaire`**, hydrates **`GET /api/user/:id`**, and chats via **`POST /api/chat`**.

**API wiring:** By default `.env.example` uses **Next.js rewrites** (`BACKEND_URL`) so the browser calls same-origin `/api/*` — no CORS setup. To call FastAPI directly, set **`NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`** in `.env.local` and ensure backend **`CORS_ORIGINS`** includes your app origin.

See `frontend/README.md` for details.

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...   # optional; stubs used if unset
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- `POST /api/submit-questionnaire` — save answers + traits + academic load (legacy `POST /api/user/questionnaire` still works).
- `POST /api/chat` — `{ "user_id", "message", "traits"? }` → `reply` + full `kv_state`.

RAG uses a **LangChain FAISS** index under `backend/rag/faiss_index/`. Build it once (requires `OPENAI_API_KEY`): `cd backend && python scripts/build_rag.py` (reads `database/questionnaire.csv` + `database/output.json`; runtime only loads the index).

See `backend/server/deployment.md` for Langflow and hosting notes.
