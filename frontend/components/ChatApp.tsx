"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  getApiBaseUrl,
  getHealth,
  postChat,
  saveQuestionnaire,
  type ChatResponseBody,
} from "@/lib/api";

import { useAuth } from "@/context/AuthContext";
import { auth } from "@/lib/firebase";
import { signOut } from "firebase/auth";

const TONES = ["friendly", "strict", "funny", "direct"] as const;

type Tone = (typeof TONES)[number];

type Msg = { role: "user" | "assistant"; text: string };

const USER_ID_KEY = "mindmap_user_id";

function loadOrCreateUserId(): string {
  if (typeof window === "undefined") return "";
  let id = localStorage.getItem(USER_ID_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(USER_ID_KEY, id);
  }
  return id;
}

export default function ChatApp() {
  const { user } = useAuth();
  const [userId, setUserId] = useState("");
  const [tone, setTone] = useState<Tone>("friendly");
  const [academicLoad, setAcademicLoad] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user?.uid) {
      setUserId(user.uid);
    } else {
      setUserId(loadOrCreateUserId());
    }
  }, [user]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await getHealth();
        if (!cancelled) setBackendOk(true);
      } catch {
        if (!cancelled) setBackendOk(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const persistProfile = useCallback(async () => {
    if (!userId.trim()) return;
    setError(null);
    try {
      await saveQuestionnaire({
        user_id: userId.trim(),
        answers: {},
        academic_load: academicLoad.trim() || null,
        traits: { tone },
      });
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2500);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save profile");
    }
  }, [userId, academicLoad, tone]);

  const send = async () => {
    const text = input.trim();
    if (!text || !userId.trim() || loading) return;
    setInput("");
    setError(null);
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);
    try {
      const data: ChatResponseBody = await postChat({
        user_id: userId.trim(),
        message: text,
        traits: { tone },
      });
      setMessages((m) => [...m, { role: "assistant", text: data.reply }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Chat request failed");
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "Something went wrong talking to the server. Is the API running?",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-0 w-full max-w-2xl flex-1 flex-col gap-4 px-4 py-6 sm:px-6">
      <header className="shrink-0 space-y-1 border-b border-zinc-200 pb-4 dark:border-zinc-800 flex justify-between items-start">
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            MindMap
          </h1>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Mental health chat — IIT KGP. API:{" "}
            <code className="rounded bg-zinc-100 px-1.5 py-0.5 text-xs dark:bg-zinc-900">
              {getApiBaseUrl()}
            </code>
          </p>
          {backendOk === false && (
            <p className="text-sm text-amber-700 dark:text-amber-400 mt-1">
              Cannot reach the backend at {getApiBaseUrl()}. Run{" "}
              <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-900">
                uvicorn app.main:app --reload
              </code>{" "}
              from the <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-900">backend</code>{" "}
              folder.
            </p>
          )}
        </div>
        {user && (
          <button
            onClick={() => signOut(auth)}
            className="text-sm font-medium text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
          >
            Sign out
          </button>
        )}
      </header>

      <section className="shrink-0 space-y-3 rounded-xl border border-zinc-200 bg-zinc-50/80 p-4 dark:border-zinc-800 dark:bg-zinc-900/40">
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex min-w-[12rem] flex-1 flex-col gap-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">
            User ID
            <input
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100"
              value={userId}
              onChange={(e) => {
                setUserId(e.target.value);
                localStorage.setItem(USER_ID_KEY, e.target.value);
              }}
            />
          </label>
          <label className="flex flex-col gap-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Tone
            <select
              className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100"
              value={tone}
              onChange={(e) => setTone(e.target.value as Tone)}
            >
              {TONES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label className="flex flex-col gap-1 text-xs font-medium text-zinc-600 dark:text-zinc-400">
          Academic load (optional, saved with profile)
          <input
            className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm text-zinc-900 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100"
            placeholder="e.g. 6th sem, dual, thesis"
            value={academicLoad}
            onChange={(e) => setAcademicLoad(e.target.value)}
          />
        </label>
        <button
          type="button"
          onClick={() => void persistProfile()}
          className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
        >
          {profileSaved ? "Saved" : "Save profile"}
        </button>
      </section>

      {error && (
        <p className="shrink-0 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800 dark:bg-red-950/50 dark:text-red-200">
          {error}
        </p>
      )}

      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.length === 0 && (
            <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
              Say hi — the assistant uses your tone and saved profile.
            </p>
          )}
          {messages.map((m, i) => (
            <div
              key={`${i}-${m.role}`}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-zinc-900 text-white dark:bg-zinc-200 dark:text-zinc-900"
                    : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl bg-zinc-100 px-4 py-2 text-sm text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400">
                Thinking…
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div className="flex gap-2 border-t border-zinc-200 p-3 dark:border-zinc-800">
          <input
            className="min-w-0 flex-1 rounded-xl border border-zinc-300 bg-white px-4 py-2.5 text-sm text-zinc-900 outline-none ring-zinc-400 focus:ring-2 dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-100"
            placeholder="Type a message…"
            value={input}
            disabled={loading}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send();
              }
            }}
          />
          <button
            type="button"
            disabled={loading || !input.trim()}
            onClick={() => void send()}
            className="shrink-0 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-700 disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
