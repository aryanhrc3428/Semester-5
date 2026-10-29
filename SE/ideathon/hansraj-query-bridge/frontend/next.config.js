/** @type {import('next').NextConfig} */
module.exports = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Proxy /api/* to the FastAPI backend so the browser talks to one origin (no CORS setup needed).
  async rewrites() {
    const api = process.env.API_URL || "http://127.0.0.1:8000";
    return [{ source: "/api/:path*", destination: `${api}/api/:path*` }];
  },
};
