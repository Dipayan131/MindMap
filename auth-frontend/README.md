# MindMap — Auth frontend (separate app)

Standalone **email + password** UI for login and registration. The main chat app stays in `../frontend/`. Your auth backend can live on another service or port.

## Run

```bash
cd auth-frontend
cp .env.example .env.local   # set NEXT_PUBLIC_AUTH_API_BASE_URL when API exists
npm install
npm run dev
```

Opens **http://localhost:3001** (avoids clashing with the chat app on 3000).

## API contract (for backend implementers)

Default JSON body for both endpoints:

**`POST {base}/auth/login`**

```json
{ "email": "user@example.com", "password": "secret" }
```

**`POST {base}/auth/register`**

```json
{ "email": "user@example.com", "password": "secret" }
```

- Successful responses should use **2xx**; the UI shows a short success message.
- Errors: return **4xx/5xx** with JSON `{ "detail": "..." }`, `{ "message": "..." }`, or `{ "error": "..." }` for a readable message.

Override paths with `NEXT_PUBLIC_AUTH_LOGIN_PATH` and `NEXT_PUBLIC_AUTH_REGISTER_PATH` if your API uses different routes.

## CORS

The auth API must allow this origin in development, e.g. `http://localhost:3001`.
