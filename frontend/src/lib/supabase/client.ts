import { createBrowserClient } from '@supabase/ssr'
import type { SupabaseClient } from '@supabase/supabase-js'

// Singleton browser client. @supabase/ssr stores the session in cookies so the
// proxy (middleware) and route handlers can read it server-side. A single
// instance avoids "Multiple GoTrueClient instances" warnings.
let client: SupabaseClient | undefined

export function createClient(): SupabaseClient {
  if (client) return client
  client = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  )
  return client
}
