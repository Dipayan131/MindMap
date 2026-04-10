import type { NextConfig } from "next";

/** FastAPI target for dev rewrites when `NEXT_PUBLIC_API_URL` is unset (same-origin, no CORS). */
const backendUrl = process.env.BACKEND_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backendUrl}/api/:path*` },
      { source: "/health", destination: `${backendUrl}/health` },
    ];
  },
};

export default nextConfig;
