import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { createServerClient } from '@supabase/ssr';
import { supabaseCookieOptions } from '@/lib/supabase/shared';

// Next.js 16 renamed the "middleware" file convention to "proxy".
// Runs for requests matched by `config.matcher` below.

const PROTECTED_PREFIXES = ['/dashboard', '/profile', '/history'];

// Behind the Caddy reverse proxy, request URLs carry the internal
// 127.0.0.1:3000 origin; build redirects from the forwarded public host so
// users aren't bounced to localhost.
function publicOrigin(request: NextRequest): string {
  const forwardedHost = request.headers.get('x-forwarded-host');
  const forwardedProto = request.headers.get('x-forwarded-proto') ?? 'https';
  if (process.env.NODE_ENV !== 'development' && forwardedHost) {
    return `${forwardedProto}://${forwardedHost}`;
  }
  return request.nextUrl.origin;
}

export async function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  // Anonymous resume routes: only allow well-formed UUIDs.
  if (pathname.startsWith('/resume/')) {
    const sessionId = pathname.split('/resume/')[1];
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!sessionId || !uuidRegex.test(sessionId)) {
      return NextResponse.redirect(`${publicOrigin(request)}/`);
    }
    return NextResponse.next();
  }

  // Refresh the Supabase session (rotating tokens into cookies) and guard
  // authenticated pages server-side.
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.SUPABASE_LOCAL_PROXY_TARGET ?? process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      // Pin the cookie name in local dev so it matches the browser client (which
      // uses a different URL via the proxy). No-op in production.
      ...(supabaseCookieOptions ? { cookieOptions: supabaseCookieOptions } : {}),
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  const {
    data: { user },
  } = await supabase.auth.getUser();

  const isProtected = PROTECTED_PREFIXES.some(
    (p) => pathname === p || pathname.startsWith(`${p}/`)
  );
  if (isProtected && !user) {
    return NextResponse.redirect(`${publicOrigin(request)}/`);
  }

  return supabaseResponse;
}

export const config = {
  matcher: ['/dashboard/:path*', '/profile/:path*', '/history/:path*', '/resume/:path*'],
};
