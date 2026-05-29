import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    const backendApiUrl = process.env.BACKEND_API_URL;
    if (!backendApiUrl) {
      throw new Error(
        "BACKEND_API_URL must be set at build time. Pass it as a Docker build ARG."
      );
    }
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendApiUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
