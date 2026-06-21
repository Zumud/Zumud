import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// OAuth (and magic-link) redirect target. Exchanges the auth `code` for a
// session, then sends the user on. The local profile row is provisioned lazily
// by the backend on the first authenticated API call.
export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/dashboard'

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  return NextResponse.redirect(`${origin}/?auth_error=oauth`)
}
