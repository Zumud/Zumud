import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Next.js 16 renamed the "middleware" file convention to "proxy".
// Runs for requests matched by `config.matcher` below.
export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Handle resume routes specifically
  if (pathname.startsWith('/resume/')) {
    const sessionId = pathname.split('/resume/')[1];

    // Validate sessionId format (should be a UUID)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    if (sessionId && uuidRegex.test(sessionId)) {
      return NextResponse.next();
    } else {
      return NextResponse.redirect(new URL('/', request.url));
    }
  }

  return NextResponse.next();
}

// Matcher is intentionally empty: this proxy is currently dormant.
// Add patterns (e.g. '/resume/:path*') to activate it.
export const config = {
  matcher: [],
};
