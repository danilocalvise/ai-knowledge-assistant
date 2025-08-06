import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Add runtime env var support for backend URL
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
  },
};

export default nextConfig;
