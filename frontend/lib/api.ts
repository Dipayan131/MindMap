/**
 * Browser → FastAPI backend. Set NEXT_PUBLIC_API_URL in .env.local (see .env.example).
 */

const defaultBase = "http://127.0.0.1:8000";

export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  return raw && raw.length > 0 ? raw.replace(/\/$/, "") : defaultBase;
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
  const res = await fetch(`${getApiBaseUrl()}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<ChatResponseBody>;
}

export async function saveQuestionnaire(
  body: QuestionnaireBody,
): Promise<UserProfileBody> {
  const res = await fetch(`${getApiBaseUrl()}/api/user/questionnaire`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<UserProfileBody>;
}

export async function getHealth(): Promise<{ status: string }> {
  const res = await fetch(`${getApiBaseUrl()}/health`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(await parseJsonError(res));
  return res.json() as Promise<{ status: string }>;
}
