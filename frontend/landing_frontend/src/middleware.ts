import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This middleware runs for all requests
export function middleware(request: NextRequest) {
  // Get the origin from the request
  const origin = request.headers.get('origin') || '';
  
  // Clone the response before modifying it
  const response = NextResponse.next();

  // Add CORS headers when the origin matches our domain or for all origins with '*'
  if (origin.includes('zumud.com') || request.nextUrl.pathname.startsWith('/_next/')) {
    response.headers.set('Access-Control-Allow-Origin', '*');
    response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    response.headers.set('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept');
  }

  return response;
}

// Configure middleware on specific paths - add more paths as needed
export const config = {
  matcher: [
    '/_next/:path*',
    '/api/:path*',
    '/applications/:path*',
  ],
}; 