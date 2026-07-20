"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { createClient } from "@/lib/supabase/client"
import { auth } from "@/lib/api"
import { Loader2, ArrowLeft, Eye, EyeOff } from "lucide-react"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

type Step = 'email' | 'password' | 'create' | 'reset-sent'

function toMessage(err: unknown, fallback: string): string {
  return err instanceof Error && err.message ? err.message : fallback
}

function GoogleIcon() {
  return (
    <svg className="h-4 w-4" viewBox="0 0 18 18" aria-hidden="true">
      <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.71-1.57 2.68-3.89 2.68-6.62z" />
      <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.71H.96v2.33A9 9 0 0 0 9 18z" />
      <path fill="#FBBC05" d="M3.97 10.71A5.41 5.41 0 0 1 3.68 9c0-.59.1-1.17.29-1.71V4.96H.96A9 9 0 0 0 0 9c0 1.45.35 2.82.96 4.04l3.01-2.33z" />
      <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.45 3.44 1.35l2.58-2.58C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.96l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z" />
    </svg>
  )
}

export default function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const supabase = createClient()

  const [step, setStep] = useState<Step>('email')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  // Separate flag so the password-reset action doesn't spin the "Sign in" button.
  const [isResetting, setIsResetting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  // Inline hint when the email belongs to a Google-only account (no password).
  const [googleHint, setGoogleHint] = useState(false)

  // Reset the flow whenever the modal opens.
  useEffect(() => {
    if (isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: refactor to key-based reset
      setStep('email')
      setPassword('')
      setShowPassword(false)
      setError(null)
      setInfo(null)
      setGoogleHint(false)
    }
  }, [isOpen])

  const resetToEmail = () => {
    setStep('email')
    setPassword('')
    setShowPassword(false)
    setError(null)
    setInfo(null)
  }

  const handleGoogle = async () => {
    setError(null)
    setInfo(null)
    setIsLoading(true)
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: `${window.location.origin}/auth/callback` },
      })
      if (error) throw error
      // Browser redirects to Google; nothing more to do here.
    } catch (err) {
      console.error('Google sign-in error:', err)
      setError(toMessage(err, 'Google sign-in failed. Please try again.'))
      setIsLoading(false)
    }
  }

  const handleEmailContinue = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setInfo(null)
    setGoogleHint(false)
    setIsLoading(true)
    try {
      const { exists, has_password } = await auth.checkEmail(email.trim())
      if (exists && has_password) {
        setStep('password')
      } else if (!exists) {
        setStep('create')
      } else {
        // Exists but no password -> a Google account. Keep them here and point
        // at the Google button instead of dead-ending on a password field.
        setGoogleHint(true)
      }
    } catch (err) {
      console.error('Email check error:', err)
      setError(toMessage(err, 'Something went wrong. Please try again.'))
    } finally {
      setIsLoading(false)
    }
  }

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      })
      if (error) throw error
      onSuccess()
    } catch (err) {
      console.error('Sign-in error:', err)
      setError(toMessage(err, 'Incorrect password. Please try again.'))
    } finally {
      setIsLoading(false)
    }
  }

  const handleForgotPassword = async () => {
    setError(null)
    setIsResetting(true)
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent('/auth/reset-password')}`,
      })
      if (error) throw error
      setStep('reset-sent')
    } catch (err) {
      console.error('Password reset error:', err)
      setError(toMessage(err, 'Could not send the reset email. Please try again.'))
    } finally {
      setIsResetting(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }
    setError(null)
    setIsLoading(true)
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password,
      })
      if (error) throw error
      if (data.session) {
        // Email confirmation disabled: signed in immediately.
        onSuccess()
      } else {
        // Email confirmation enabled (requires SMTP): no session yet.
        setInfo('Account created. Please check your email to confirm, then sign in.')
        setStep('email')
        setIsLoading(false)
      }
    } catch (err) {
      console.error('Sign-up error:', err)
      setError(toMessage(err, 'Could not create your account. Please try again.'))
      setIsLoading(false)
    }
  }

  const inputClass = "field mt-1.5"

  const emailPill = (
    <button
      type="button"
      onClick={resetToEmail}
      className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
    >
      <ArrowLeft className="h-4 w-4" />
      <span className="truncate max-w-[16rem]">{email.trim()}</span>
    </button>
  )

  const passwordField = (id: string, label: string, autoComplete: string) => (
    <div>
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={showPassword ? 'text' : 'password'}
          required
          autoFocus
          autoComplete={autoComplete}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={`${inputClass} pr-10`}
        />
        <button
          type="button"
          onClick={() => setShowPassword((s) => !s)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
          className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted-foreground transition-colors hover:text-foreground"
        >
          {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </div>
    </div>
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            {step === 'email' && 'Welcome to Zumud'}
            {step === 'password' && 'Welcome back'}
            {step === 'create' && 'Create your account'}
            {step === 'reset-sent' && 'Check your email'}
          </DialogTitle>
        </DialogHeader>

        {error && (
          <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {info && (
          <div className="rounded-lg border border-brand/30 bg-brand/10 px-4 py-3 text-sm text-brand" role="status">
            <span className="block sm:inline">{info}</span>
          </div>
        )}

        {step === 'email' && (
          <div className="space-y-4">
            <Button
              type="button"
              variant="outline"
              disabled={isLoading}
              onClick={handleGoogle}
              className="w-full"
            >
              <span className="mr-2 inline-flex"><GoogleIcon /></span>
              Continue with Google
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-border" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="bg-background px-2 text-muted-foreground">or</span>
              </div>
            </div>

            <form onSubmit={handleEmailContinue} className="space-y-4">
              <div>
                <label htmlFor="auth-email" className="block text-sm font-medium">
                  Email
                </label>
                <input
                  id="auth-email"
                  type="email"
                  required
                  autoFocus
                  autoComplete="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    setGoogleHint(false)
                  }}
                  className={inputClass}
                  placeholder="you@example.com"
                />
              </div>

              {googleHint && (
                <p className="text-sm text-muted-foreground">
                  This email uses Google sign-in. Tap{' '}
                  <span className="font-medium text-foreground">Continue with Google</span> above.
                </p>
              )}

              <Button
                type="submit"
                variant="brand"
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Please wait...
                  </>
                ) : (
                  'Continue'
                )}
              </Button>
            </form>
          </div>
        )}

        {step === 'password' && (
          <form onSubmit={handleSignIn} className="space-y-4">
            {emailPill}
            {passwordField('signin-password', 'Password', 'current-password')}
            <Button
              type="submit"
              variant="brand"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
            <button
              type="button"
              onClick={handleForgotPassword}
              disabled={isLoading || isResetting}
              className="block w-full text-center text-sm text-muted-foreground transition-colors hover:text-foreground disabled:opacity-50"
            >
              Forgot password?
            </button>
          </form>
        )}

        {step === 'create' && (
          <form onSubmit={handleCreate} className="space-y-4">
            {emailPill}
            {passwordField('create-password', 'Password', 'new-password')}
            <p className="text-xs text-muted-foreground">Password must be at least 6 characters</p>
            <Button
              type="submit"
              variant="brand"
              disabled={isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                'Create account'
              )}
            </Button>
          </form>
        )}

        {step === 'reset-sent' && (
          <div className="space-y-3">
            <button
              type="button"
              onClick={() => { setError(null); setStep('password') }}
              className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to sign in
            </button>
            <p className="text-sm text-muted-foreground">
              We sent a password reset link to{' '}
              <span className="font-medium text-foreground">{email.trim()}</span>. Open it to choose a new password.
            </p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
