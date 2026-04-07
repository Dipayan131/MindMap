import LoginForm from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <LoginForm />
      <p className="mt-8 max-w-sm text-center text-xs text-zinc-400 dark:text-zinc-500">
        Auth API is separate from the chat app. Runs on port{" "}
        <strong className="text-zinc-600 dark:text-zinc-400">3001</strong> by default.
      </p>
    </div>
  );
}
