// Shared Supabase client configuration.
//
// In local dev, supabase-js in the browser is routed through the Next dev origin
// (NEXT_PUBLIC_SUPABASE_URL=http://localhost:3000) because the Docker-published
// Supabase port isn't reachable from the host browser under WSL; server-side code
// reaches Supabase directly. @supabase/ssr derives the auth cookie name from the
// client URL, so those two different URLs would otherwise produce different cookie
// names and the server couldn't read the browser's session. Pin one shared cookie
// name in local dev. In production both sides use the same real Supabase URL, so we
// leave @supabase/ssr's default untouched (no production behavior change).
const isLocalProxy = (process.env.NEXT_PUBLIC_SUPABASE_URL ?? '').startsWith('http://localhost')

export const supabaseCookieOptions: { name: string } | undefined = isLocalProxy
  ? { name: 'sb-localhost-auth-token' }
  : undefined
