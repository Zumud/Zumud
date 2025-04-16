import type { NextConfig } from "next";

// Using type assertion to avoid TypeScript errors with new config options
const nextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/applications/:path*',
        destination: 'http://localhost:8000/applications/:path*',
      },
    ];
  },
  
  // Configuration to resolve cross-origin warning
  experimental: {
    allowedDevOrigins: ['zumud.com'],
  },
} as NextConfig;

export default nextConfig;
