"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { auth } from "@/lib/api"
import { setAccessToken, setUserData } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>('login')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Login form state
  const [loginUsername, setLoginUsername] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  
  // Signup form state
  const [signupUsername, setSignupUsername] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [initialResume, setInitialResume] = useState('')
  
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    
    try {
      const result = await auth.login(loginUsername, loginPassword)
      
      if (!result || !result.access_token) {
        throw new Error('Invalid response from server')
      }
      
      setAccessToken(result.access_token)
      setUserData({
        username: result.username,
        id: result.user_id
      })
      onSuccess()
    } catch (err: any) {
      console.error('Login error:', err)
      setError(typeof err === 'string' ? err : err.message || 'Login failed. Please check your credentials.')
    } finally {
      setIsLoading(false)
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
    
    try {
      const result = await auth.signup(
        signupUsername, 
        signupPassword, 
        signupEmail, 
        initialResume
      )
      
      if (result) {
        setError(null)
        // Clear signup form
        setSignupUsername('')
        setSignupPassword('')
        setSignupEmail('')
        setInitialResume('')
        
        // Switch to login tab
        setActiveTab('login')
        setIsLoading(false)
        alert('Account created successfully! Please log in.')
      }
    } catch (err: any) {
      console.error('Signup error:', err)
      setError(typeof err === 'string' ? err : err.message || 'Signup failed. Please try again.')
      setIsLoading(false)
    }
  }
  
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
        
        {activeTab === 'login' ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label htmlFor="login-username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="login-username"
                type="text"
                required
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
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
        ) : (
          <form onSubmit={handleSignup} className="space-y-4">
            <div>
              <label htmlFor="signup-username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="signup-username"
                type="text"
                required
                value={signupUsername}
                onChange={(e) => setSignupUsername(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
              />
            </div>
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
              <label htmlFor="initial-resume" className="block text-sm font-medium text-gray-700">
                Your Initial Resume (optional)
              </label>
              <textarea
                id="initial-resume"
                rows={5}
                value={initialResume}
                onChange={(e) => setInitialResume(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500"
                placeholder="Paste your current resume content here..."
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
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
} 