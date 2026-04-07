import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MindMap — Sign in",
  description: "Email and password authentication for MindMap.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
