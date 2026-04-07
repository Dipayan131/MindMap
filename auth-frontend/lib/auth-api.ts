/**
 * Contract for your auth backend (to be implemented separately).
 *
 * Defaults:
 *   POST {base}/auth/login    { "email", "password" }
 *   POST {base}/auth/register { "email", "password" }
 *
 * Override paths with NEXT_PUBLIC_AUTH_LOGIN_PATH / NEXT_PUBLIC_AUTH_REGISTER_PATH.
 */

export function getAuthApiBase(): string {
  const raw = process.env.NEXT_PUBLIC_AUTH_API_BASE_URL?.trim();
  return raw ? raw.replace(/\/$/, "") : "";
}

export function getLoginPath(): string {
  const p = process.env.NEXT_PUBLIC_AUTH_LOGIN_PATH?.trim();
  return p && p.startsWith("/") ? p : "/auth/login";
}

export function getRegisterPath(): string {
  const p = process.env.NEXT_PUBLIC_AUTH_REGISTER_PATH?.trim();
  return p && p.startsWith("/") ? p : "/auth/register";
}

async function parseErrorMessage(res: Response): Promise<string> {
  try {
    const data = (await res.json()) as {
      detail?: unknown;
      message?: unknown;
      error?: unknown;
    };
    if (typeof data.detail === "string") return data.detail;
    if (typeof data.message === "string") return data.message;
    if (typeof data.error === "string") return data.error;
  } catch {
    /* ignore */
  }
  return res.statusText || `HTTP ${res.status}`;
}

export class AuthApiNotConfiguredError extends Error {
  constructor() {
    super(
      "Auth API is not configured. Set NEXT_PUBLIC_AUTH_API_BASE_URL in .env.local (see .env.example).",
    );
    this.name = "AuthApiNotConfiguredError";
  }
}

export async function requestLogin(email: string, password: string): Promise<Response> {
  const base = getAuthApiBase();
  if (!base) throw new AuthApiNotConfiguredError();
  return fetch(`${base}${getLoginPath()}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function requestRegister(
  email: string,
  password: string,
): Promise<Response> {
  const base = getAuthApiBase();
  if (!base) throw new AuthApiNotConfiguredError();
  return fetch(`${base}${getRegisterPath()}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function assertOk(res: Response): Promise<void> {
  if (!res.ok) throw new Error(await parseErrorMessage(res));
}
