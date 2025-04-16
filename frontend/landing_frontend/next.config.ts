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
  
  // Optimize images for better performance
  images: {
    domains: ['zumud.com'],
    formats: ['image/avif', 'image/webp'],
  },
  
  // Add only essential CORS headers
  async headers() {
    return [
      // CORS headers for static assets
      {
        source: '/_next/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET' },
        ],
      },
    ];
  },
} as NextConfig;

export default nextConfig;
