import { NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase/server'

// Behind the Caddy reverse proxy, request.url's origin is the internal
// 127.0.0.1:3000 address, so redirects built from it would send users to
// localhost. In production we trust the forwarded host (the public domain).
function publicBase(request: Request, origin: string): string {
  const forwardedHost = request.headers.get('x-forwarded-host')
  const forwardedProto = request.headers.get('x-forwarded-proto') ?? 'https'
  if (process.env.NODE_ENV !== 'development' && forwardedHost) {
    return `${forwardedProto}://${forwardedHost}`
  }
  return origin
}

// OAuth (and magic-link) redirect target. Exchanges the auth `code` for a
// session, then sends the user on. The local profile row is provisioned lazily
// by the backend on the first authenticated API call.
export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  let next = searchParams.get('next') ?? '/dashboard'
  // Only allow internal redirects (avoid open-redirects via ?next=).
  if (!next.startsWith('/')) next = '/dashboard'

  const base = publicBase(request, origin)

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      return NextResponse.redirect(`${base}${next}`)
    }
  }

  return NextResponse.redirect(`${base}/?auth_error=oauth`)
}
