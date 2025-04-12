import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/applications/:path*',
        destination: 'http://gettailoredresume.com:8000/applications/:path*',
      },
    ];
  },
};

export default nextConfig;
