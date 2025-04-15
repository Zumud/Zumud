import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/applications/:path*',
        destination: 'https://zumud.com:8000/applications/:path*',
      },
    ];
  },
};

export default nextConfig;
