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
  
  // Configuration to allow cross-origin requests in both dev and production
  experimental: {
    allowedDevOrigins: ['zumud.com'],
  },
  
  // Optimize images for better performance
  images: {
    domains: ['zumud.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Add security and CORS headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
      // Add CORS headers for production
      {
        source: '/_next/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: 'https://zumud.com' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'X-Requested-With, Content-Type, Accept' }
        ]
      }
    ];
  },
} as NextConfig;

export default nextConfig;
