import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This middleware runs for all requests
export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  
  // Handle resume routes specifically
  if (pathname.startsWith('/resume/')) {
    const sessionId = pathname.split('/resume/')[1];
    
    // Validate sessionId format (should be a UUID)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    
    if (sessionId && uuidRegex.test(sessionId)) {
      // Valid sessionId - allow the request to proceed to the dynamic route
      console.log(`[Middleware] Valid resume route: ${pathname}`);
      return NextResponse.next();
    } else {
      // Invalid sessionId - redirect to home
      console.log(`[Middleware] Invalid sessionId, redirecting: ${sessionId}`);
      return NextResponse.redirect(new URL('/', request.url));
    }
  }
  
  // Handle other routes normally
  return NextResponse.next();
}

// Temporarily disable middleware to test if it's causing 404 issues
export const config = {
  matcher: [
    // Commenting out to disable middleware
    // '/resume/:path*',
  ],
}; 