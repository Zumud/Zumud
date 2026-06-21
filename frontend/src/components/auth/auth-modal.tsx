"use client"

import { useState, useRef, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { createClient } from "@/lib/supabase/client"
import { resume } from "@/lib/api"
import { Loader2, Upload, FileText, AlertCircle, CheckCircle, PlusCircle } from "lucide-react"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  defaultTab?: 'login' | 'signup'
}

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

export default function AuthModal({ isOpen, onClose, onSuccess, defaultTab = 'login' }: AuthModalProps) {
  const supabase = createClient()

  const [activeTab, setActiveTab] = useState<'login' | 'signup'>(defaultTab)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [resumeMethod, setResumeMethod] = useState<'none' | 'upload' | 'paste'>('none')

  // Login form state
  const [loginEmail, setLoginEmail] = useState('')
  const [loginPassword, setLoginPassword] = useState('')

  // Signup form state
  const [signupEmail, setSignupEmail] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [initialResume, setInitialResume] = useState('')
  const [resumeFileObj, setResumeFileObj] = useState<File | null>(null)
  const [resumeFileName, setResumeFileName] = useState<string | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')

  const fileInputRef = useRef<HTMLInputElement>(null)

  // Reset to default tab when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab(defaultTab)
      setError(null)
      setInfo(null)
    }
  }, [isOpen, defaultTab])

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
      // On success the browser is redirected to Google; nothing more to do here.
    } catch (err) {
      console.error('Google sign-in error:', err)
      setError(toMessage(err, 'Google sign-in failed. Please try again.'))
      setIsLoading(false)
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setInfo(null)

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: loginEmail.trim(),
        password: loginPassword,
      })
      if (error) throw error
      onSuccess()
    } catch (err) {
      console.error('Login error:', err)
      setError(toMessage(err, 'Login failed. Please check your credentials.'))
    } finally {
      setIsLoading(false)
    }
  }

  // Attach an optional resume right after signup, once a session exists.
  // Non-fatal: a failure here shouldn't block account creation.
  const attachInitialResume = async () => {
    try {
      if (resumeFileObj) {
        await resume.uploadResumePdf(resumeFileObj)
      } else if (initialResume.trim()) {
        await resume.updateResume(initialResume.trim())
      }
    } catch (err) {
      console.error('Failed to attach initial resume:', err)
    }
  }

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()

    if (signupPassword.length < 6) {
      setError('Password must be at least 6 characters long')
      return
    }

    setIsLoading(true)
    setError(null)
    setInfo(null)

    try {
      const { data, error } = await supabase.auth.signUp({
        email: signupEmail.trim(),
        password: signupPassword,
      })
      if (error) throw error

      if (data.session) {
        // Email confirmation disabled: the user is signed in immediately.
        await attachInitialResume()
        onSuccess()
      } else {
        // Email confirmation enabled: no session yet.
        setActiveTab('login')
        setInfo('Account created. Please check your email to confirm your address, then log in.')
        setIsLoading(false)
      }
    } catch (err) {
      console.error('Signup error:', err)
      setError(toMessage(err, 'Signup failed. Please try again.'))
      setIsLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadStatus('uploading')
    setError(null)

    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file')
      setUploadStatus('error')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB limit')
      setUploadStatus('error')
      return
    }

    setResumeFileName(file.name)
    setResumeFileObj(file)
    setUploadStatus('success')
    setResumeMethod('upload')
  }

  const clearResumeFile = () => {
    setResumeFileObj(null)
    setResumeFileName(null)
    setUploadStatus('idle')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleResumeMethodChange = (method: 'upload' | 'paste') => {
    if (method === 'upload') {
      setInitialResume('')
      setResumeMethod('upload')
      fileInputRef.current?.click()
    } else {
      clearResumeFile()
      setResumeMethod('paste')
    }
  }

  const renderResumeUploadButton = () => (
    <button
      type="button"
      className={cn(
        "flex flex-col items-center justify-center p-4 border-2 rounded-lg text-center transition-all",
        resumeMethod === 'upload'
          ? "border-emerald-500 bg-emerald-50 text-emerald-700"
          : "border-gray-200 hover:border-emerald-200 hover:bg-emerald-50/50 text-gray-600 hover:text-emerald-600"
      )}
      onClick={() => handleResumeMethodChange('upload')}
    >
      <Upload
        className={cn(
          "h-10 w-10 mb-2",
          resumeMethod === 'upload' ? "text-emerald-500" : "text-gray-400"
        )}
      />
      <span className="text-sm font-medium">Upload PDF Resume</span>
      <p className="text-xs mt-1 text-gray-500">We&apos;ll extract the text automatically</p>
    </button>
  )

  const renderResumeTextButton = () => (
    <button
      type="button"
      className={cn(
        "flex flex-col items-center justify-center p-4 border-2 rounded-lg text-center transition-all",
        resumeMethod === 'paste'
          ? "border-emerald-500 bg-emerald-50 text-emerald-700"
          : "border-gray-200 hover:border-emerald-200 hover:bg-emerald-50/50 text-gray-600 hover:text-emerald-600"
      )}
      onClick={() => handleResumeMethodChange('paste')}
    >
      <FileText
        className={cn(
          "h-10 w-10 mb-2",
          resumeMethod === 'paste' ? "text-emerald-500" : "text-gray-400"
        )}
      />
      <span className="text-sm font-medium">Enter Resume Text</span>
      <p className="text-xs mt-1 text-gray-500">Type or paste your resume content</p>
    </button>
  )

  const renderResumeInput = () => {
    switch (resumeMethod) {
      case 'upload':
        return (
          <div className="mt-4 border rounded-lg">
            <div className="p-4">
              {uploadStatus === 'success' ? (
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <CheckCircle className="h-8 w-8 text-emerald-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {resumeFileName}
                    </p>
                    <p className="text-xs text-emerald-600">
                      PDF ready. Text will be extracted after sign-up.
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        clearResumeFile()
                        fileInputRef.current?.click()
                      }}
                    >
                      Replace
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        clearResumeFile()
                        setResumeMethod('none')
                      }}
                    >
                      Remove
                    </Button>
                  </div>
                </div>
              ) : uploadStatus === 'error' ? (
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <AlertCircle className="h-8 w-8 text-red-500" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-red-700">Upload failed</p>
                    <p className="text-xs text-red-600">
                      {error || "Please try again with a different file."}
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setUploadStatus('idle')
                        fileInputRef.current?.click()
                      }}
                    >
                      Try Again
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-6">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="application/pdf"
                    className="hidden"
                    onChange={handleFileChange}
                  />
                  <button
                    type="button"
                    className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-emerald-100 text-emerald-600 mb-3"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="h-6 w-6" />
                  </button>
                  <p className="text-sm text-gray-700">
                    <button
                      type="button"
                      className="font-medium text-emerald-600 hover:text-emerald-500"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Click to upload
                    </button> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500 mt-1">PDF up to 5MB</p>
                </div>
              )}
            </div>
          </div>
        )
      case 'paste':
        return (
          <div className="mt-4">
            <textarea
              id="resume-text"
              rows={6}
              value={initialResume}
              onChange={(e) => setInitialResume(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 text-sm"
              placeholder="Type or paste your resume content here..."
            />
            <p className="mt-1 text-xs text-gray-500">
              Include your skills, experience, education, and any other relevant information
            </p>
          </div>
        )
      default:
        return null
    }
  }

  const renderGoogleButton = (label: string) => (
    <>
      <Button
        type="button"
        variant="outline"
        disabled={isLoading}
        onClick={handleGoogle}
        className="w-full border-gray-300 text-gray-700 hover:bg-gray-50"
      >
        <span className="mr-2 inline-flex"><GoogleIcon /></span>
        {label}
      </Button>
      <div className="relative my-4">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-2 text-gray-400">or</span>
        </div>
      </div>
    </>
  )

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>
            <div className="flex border-b">
              <button
                className={cn(
                  "px-4 py-2 text-sm font-medium",
                  activeTab === "login" ? "border-b-2 border-emerald-600 text-emerald-600" : "text-gray-500"
                )}
                onClick={() => setActiveTab("login")}
              >
                Login
              </button>
              <button
                className={cn(
                  "px-4 py-2 text-sm font-medium",
                  activeTab === "signup" ? "border-b-2 border-emerald-600 text-emerald-600" : "text-gray-500"
                )}
                onClick={() => setActiveTab("signup")}
              >
                Sign Up
              </button>
            </div>
          </DialogTitle>
        </DialogHeader>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {info && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded relative" role="status">
            <span className="block sm:inline">{info}</span>
          </div>
        )}

        {activeTab === 'login' ? (
          <div className="space-y-2">
            {renderGoogleButton('Continue with Google')}
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label htmlFor="login-email" className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <input
                  id="login-email"
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
              <div>
                <label htmlFor="login-password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  id="login-password"
                  type="password"
                  required
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-emerald-600 hover:bg-emerald-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Logging in...
                  </>
                ) : (
                  "Login"
                )}
              </Button>
            </form>
          </div>
        ) : (
          <div className="space-y-2">
            {renderGoogleButton('Sign up with Google')}
            <form onSubmit={handleSignup} className="space-y-4">
              <div>
                <label htmlFor="signup-email" className="block text-sm font-medium text-gray-700">
                  Email
                </label>
                <input
                  id="signup-email"
                  type="email"
                  required
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
              </div>
              <div>
                <label htmlFor="signup-password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <input
                  id="signup-password"
                  type="password"
                  required
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                />
                <p className="mt-1 text-xs text-gray-500">Password must be at least 6 characters</p>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-medium text-gray-700">Your Resume</h3>
                  <span className="text-xs text-gray-500">Optional</span>
                </div>

                {resumeMethod === 'none' ? (
                  <div className="grid grid-cols-2 gap-4">
                    {renderResumeUploadButton()}
                    {renderResumeTextButton()}
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-center">
                      <h4 className="text-sm font-medium text-emerald-700">
                        {resumeMethod === 'upload' ? 'Resume PDF' : 'Resume Text'}
                      </h4>
                      <button
                        type="button"
                        className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
                        onClick={() => {
                          setResumeMethod('none')
                          clearResumeFile()
                          setInitialResume('')
                        }}
                      >
                        <PlusCircle className="h-3 w-3 rotate-45" />
                        <span>Change method</span>
                      </button>
                    </div>
                    {renderResumeInput()}
                  </div>
                )}
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-emerald-600 hover:bg-emerald-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  "Create Account"
                )}
              </Button>
            </form>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
