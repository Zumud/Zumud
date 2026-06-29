import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import { supabaseCookieOptions } from './shared'

// Server-side Supabase client for Route Handlers / Server Components. Reads and
// writes the session cookies via Next's cookie store (async in Next 16).
export async function createClient() {
  const cookieStore = await cookies()

  return createServerClient(
    // Server-side reaches Supabase directly (in local dev, the Docker URL via
    // SUPABASE_LOCAL_PROXY_TARGET), bypassing the browser same-origin proxy.
    process.env.SUPABASE_LOCAL_PROXY_TARGET ?? process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      // Pin the cookie name in local dev so it matches the browser client (which
      // uses a different URL via the proxy). No-op in production.
      ...(supabaseCookieOptions ? { cookieOptions: supabaseCookieOptions } : {}),
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // Called from a Server Component where cookies are read-only; the
            // proxy refreshes the session, so this can be safely ignored.
          }
        },
      },
    }
  )
}
