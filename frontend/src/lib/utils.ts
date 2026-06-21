import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { createClient } from "@/lib/supabase/client"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Auth utilities, backed by Supabase Auth. The session is managed by
// @supabase/ssr (stored in cookies); these helpers expose the bits the app
// needs: the bearer token for backend calls, a login check, and sign-out.
export async function getAccessToken(): Promise<string | null> {
  const supabase = createClient()
  const { data } = await supabase.auth.getSession()
  return data.session?.access_token ?? null
}

export async function isAuthenticated(): Promise<boolean> {
  const supabase = createClient()
  const { data } = await supabase.auth.getSession()
  return !!data.session
}

export async function signOut(): Promise<void> {
  const supabase = createClient()
  await supabase.auth.signOut()
}
