import LoginForm from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <LoginForm />
      <p className="mt-8 max-w-sm text-center text-xs text-zinc-400 dark:text-zinc-500">
        Sign in with Firebase (email/password or Google). Set the{" "}
        <code className="text-zinc-500 dark:text-zinc-400">NEXT_PUBLIC_FIREBASE_*</code>{" "}
        variables in <code className="text-zinc-500 dark:text-zinc-400">.env.local</code>.
      </p>
    </div>
  );
}
