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

  // Enable static site generation for improved SEO
  output: 'export',
  
  // Optimize images for better performance
  images: {
    domains: ['zumud.com'],
    formats: ['image/avif', 'image/webp'],
  },

  // Add security headers
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
    ];
  },
} as NextConfig;

export default nextConfig;
