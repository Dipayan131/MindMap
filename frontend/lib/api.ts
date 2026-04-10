/**
 * Browser → FastAPI backend.
 *
 * - If `NEXT_PUBLIC_API_URL` is set: calls that origin (ensure FastAPI `CORS_ORIGINS` includes your app).
 * - If unset/empty: uses same-origin paths `/api/*` and `/health` → proxied by `next.config.ts` to `BACKEND_URL`.
 */

const defaultDirectBase = "http://127.0.0.1:8000";

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (raw && raw.length > 0) {
    return raw.replace(/\/$/, "");
  }
  return "";
}

function apiUrl(path: string): string {
  const base = getApiBaseUrl();
  const p = path.startsWith("/") ? path : `/${path}`;
  return base ? `${base}${p}` : p;
}

export type ChatTraits = Record<string, unknown>;

export type ChatRequestBody = {
  user_id: string;
  message: string;
  traits?: ChatTraits;
};

export type ChatResponseBody = {
  reply: string;
  kv_state: Record<string, unknown>;
  prompts_version: string;
};

export type QuestionnaireBody = {
  user_id: string;
  answers?: Record<string, unknown>;
  academic_load?: string | null;
  traits?: ChatTraits;
};

export type UserProfileBody = {
  user_id: string;
  questionnaire: Record<string, unknown>;
  academic_load: string | null;
  traits: Record<string, unknown>;
};

export type QuestionnaireRow = {
  id: string;
  question: string;
  category: string;
};

export type QuestionnaireTemplateResponse = {
  questions: QuestionnaireRow[];
};

export type SetTraitsBody = {
  user_id: string;
  tone?: string | null;
  style?: string | null;
  traits?: ChatTraits;
};

async function parseJsonError(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as { detail?: unknown };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return JSON.stringify(data.detail);
  } catch {
    /* ignore */
  }
  return res.statusText || `HTTP ${res.status}`;
}

export async function postChat(body: ChatRequestBody): Promise<ChatResponseBody> {
  const res = await fetch(apiUrl("/api/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<ChatResponseBody>;
}

/** Save questionnaire answers + optional academic load + traits (POST /api/submit-questionnaire or legacy path). */
export async function saveQuestionnaire(
  body: QuestionnaireBody,
): Promise<UserProfileBody> {
  const res = await fetch(apiUrl("/api/submit-questionnaire"), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<UserProfileBody>;
}

/** Update tone/style only without wiping questionnaire (POST /api/set-traits). */
export async function setTraits(body: SetTraitsBody): Promise<UserProfileBody> {
  const res = await fetch(apiUrl("/api/set-traits"), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<UserProfileBody>;
}

/** Load rows from backend `database/questionnaire.csv` for onboarding UI. */
export async function getQuestionnaireTemplate(): Promise<QuestionnaireTemplateResponse> {
  const res = await fetch(apiUrl("/api/questionnaire"), {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<QuestionnaireTemplateResponse>;
}

/** Hydrate saved profile (GET /api/user/:user_id). */
export async function getUserProfile(userId: string): Promise<UserProfileBody> {
  const res = await fetch(apiUrl(`/api/user/${encodeURIComponent(userId)}`), {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<UserProfileBody>;
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(apiUrl("/health"), {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<{ status: string }>;
}
