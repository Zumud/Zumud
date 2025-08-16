import type { NextConfig } from "next";

// Using type assertion to avoid TypeScript errors with new config options
const nextConfig = {
  /* config options here */
  // Disable ESLint during production builds
  eslint: {
    ignoreDuringBuilds: true,
  },
  // Disable TypeScript errors during builds
  typescript: {
    ignoreBuildErrors: true,
  },
  // Make environment variables available to the client
  env: {
    NEXT_PUBLIC_API_URL: process.env.API_URL,
  },
  // Increase the proxy timeout for API requests to 120 seconds (default is 30s)
  experimental: {
    proxyTimeout: 120000, // 120 seconds in milliseconds
  },
  async rewrites() {
    const apiUrl = process.env.API_URL || 'http://localhost:8000';
    console.log('Next.js rewrites configured with API_URL:', apiUrl);
    return [
      {
        source: '/applications/:path*',
        destination: `${apiUrl}/applications/:path*`,
      },
      {
        source: '/login',
        destination: `${apiUrl}/login`,
      },
      {
        source: '/users/:path*',
        destination: `${apiUrl}/users/:path*`,
      },
      {
        source: '/billing/:path*',
        destination: `${apiUrl}/billing/:path*`,
      },
      {
        source: '/ingest/static/:path*',
        destination: 'https://eu-assets.i.posthog.com/static/:path*',
      },
      {
        source: '/ingest/:path*',
        destination: 'https://eu.i.posthog.com/:path*',
      },
      {
        source: '/ingest/decide',
        destination: 'https://eu.i.posthog.com/decide',
      },
    ];
  },

  // This is required to support PostHog trailing slash API requests
  skipTrailingSlashRedirect: true,

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
