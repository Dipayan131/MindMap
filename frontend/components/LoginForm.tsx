"use client";

import Link from "next/link";
import { useState } from "react";
import { signInWithEmailAndPassword, signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email.trim(), password);
      setMessage("Signed in successfully.");
      router.push("/");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to sign in");
      } else {
        setError("Failed to sign in");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogleSignIn() {
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      await signInWithPopup(auth, googleProvider);
      setMessage("Signed in with Google successfully.");
      router.push("/");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message || "Failed to sign in with Google");
      } else {
        setError("Failed to sign in with Google");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={(e) => void onSubmit(e)}
      className="w-full max-w-sm space-y-5 rounded-2xl border border-zinc-200 bg-white p-8 shadow-sm dark:border-zinc-800 dark:bg-zinc-950"
    >
      <div className="space-y-1 text-center">
        <h1 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">
          Sign in
        </h1>
        <p className="text-sm text-zinc-500 dark:text-zinc-400">
          MindMap — use your email and password
        </p>
      </div>

      <label className="block space-y-1.5 text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Email
        <input
          name="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-xl border border-zinc-300 bg-white px-3 py-2.5 text-zinc-900 outline-none ring-violet-500 focus:ring-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
          placeholder="you@example.com"
        />
      </label>

      <label className="block space-y-1.5 text-sm font-medium text-zinc-700 dark:text-zinc-300">
        Password
        <div className="relative">
          <input
            name="password"
            type={showPassword ? "text" : "password"}
            autoComplete="current-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-zinc-300 bg-white px-3 py-2.5 pr-24 text-zinc-900 outline-none ring-violet-500 focus:ring-2 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-100"
            placeholder="••••••••"
          />
          <button
            type="button"
            onClick={() => setShowPassword((s) => !s)}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg px-2 py-1 text-xs font-medium text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800"
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>
      </label>

      {error && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </p>
      )}
      {message && (
        <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-200">
          {message}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-xl bg-violet-600 py-2.5 text-sm font-semibold text-white transition hover:bg-violet-700 disabled:opacity-50 dark:bg-violet-500 dark:hover:bg-violet-600"
      >
        {loading ? "Signing in…" : "Sign in"}
      </button>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-zinc-200 dark:border-zinc-800"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-2 text-zinc-500 dark:bg-zinc-950 dark:text-zinc-400">
            Or continue with
          </span>
        </div>
      </div>

      <button
        type="button"
        disabled={loading}
        onClick={handleGoogleSignIn}
        className="w-full rounded-xl border border-zinc-300 bg-white py-2.5 text-sm font-semibold text-zinc-700 transition hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800 flex items-center justify-center gap-2"
      >
        <svg viewBox="0 0 24 24" className="h-5 w-5" aria-hidden="true">
          <path d="M12.0003 4.75C13.7703 4.75 15.3553 5.36 16.6053 6.549L20.0303 3.125C17.9503 1.19 15.2353 0 12.0003 0C7.31028 0 3.25528 2.69 1.28028 6.609L5.27028 9.704C6.21528 6.86 8.87028 4.75 12.0003 4.75Z" fill="#EA4335"/>
          <path d="M23.49 12.275C23.49 11.49 23.415 10.73 23.3 10H12V14.51H18.47C18.18 15.99 17.34 17.25 16.08 18.1L19.945 21.1C22.2 19.01 23.49 15.92 23.49 12.275Z" fill="#4285F4"/>
          <path d="M5.26498 14.294C5.02498 13.569 4.88501 12.799 4.88501 12C4.88501 11.201 5.02498 10.431 5.26498 9.706L1.275 6.611C0.46 8.226 0 10.061 0 12C0 13.939 0.46 15.774 1.275 17.389L5.26498 14.294Z" fill="#FBBC05"/>
          <path d="M12.0004 24C15.2404 24 17.9654 22.935 19.9454 21.095L16.0804 18.095C15.0054 18.82 13.6204 19.245 12.0004 19.245C8.87037 19.245 6.21537 17.135 5.26537 14.29L1.27539 17.385C3.25539 21.31 7.31037 24 12.0004 24Z" fill="#34A853"/>
        </svg>
        Sign in with Google
      </button>

      <p className="text-center text-sm text-zinc-500 dark:text-zinc-400">
        No account?{" "}
        <Link
          href="/register"
          className="font-medium text-violet-600 hover:underline dark:text-violet-400"
        >
          Create one
        </Link>
      </p>
    </form>
  );
}
