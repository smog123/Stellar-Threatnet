/** @type {import('next').NextConfig} */
const BACKEND_ORIGIN =
  process.env.BACKEND_ORIGIN ?? "https://stellar-threatnet-api.onrender.com";

const nextConfig = {
  reactStrictMode: true,
  // `standalone` is only needed for the Docker image; on Vercel it collides
  // with the platform build adapter (ENOENT .next/next-server.js.nft.json on
  // Next 16.3) — see vercel/next.js#96646.
  output: process.env.VERCEL ? undefined : "standalone",
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }],
  },
  async rewrites() {
    // Proxy API calls through the frontend origin so browser requests are
    // same-origin (no CORS) and independent of the backend's allowlist.
    return [
      {
        source: "/api/v1/:path*",
        destination: `${BACKEND_ORIGIN}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
