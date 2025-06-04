"use client"

import { useState, useRef, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { auth } from "@/lib/api"
import { setAccessToken, setUserData } from "@/lib/utils"
import { Loader2, Upload, FileText, X, AlertCircle, CheckCircle, PlusCircle } from "lucide-react"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
  defaultTab?: 'login' | 'signup'
}

export default function AuthModal({ isOpen, onClose, onSuccess, defaultTab = 'login' }: AuthModalProps) {
  const [activeTab, setActiveTab] = useState<'login' | 'signup'>(defaultTab)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [resumeMethod, setResumeMethod] = useState<'none' | 'upload' | 'paste'>('none')
  
  // Login form state
  const [loginUsername, setLoginUsername] = useState('')
  const [loginPassword, setLoginPassword] = useState('')
  
  // Signup form state
  const [signupUsername, setSignupUsername] = useState('')
  const [signupPassword, setSignupPassword] = useState('')
  const [signupEmail, setSignupEmail] = useState('')
  const [initialResume, setInitialResume] = useState('')
  const [resumeFile, setResumeFile] = useState<string | null>(null)
  const [resumeFileName, setResumeFileName] = useState<string | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Reset to default tab when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveTab(defaultTab)
    }
  }, [isOpen, defaultTab])
  
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
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    // Reset upload status
    setUploadStatus('uploading')
    setError(null)
    
    // Check if the file is a PDF
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file')
      setUploadStatus('error')
      return
    }
    
    // Check if the file is too large (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB limit')
      setUploadStatus('error')
      return
    }
    
    setResumeFileName(file.name)
    
    // Convert file to base64
    const reader = new FileReader()
    reader.onload = () => {
      setResumeFile(reader.result as string)
      setUploadStatus('success')
      // Set method to upload if not already
      setResumeMethod('upload')
    }
    reader.onerror = () => {
      setError('Failed to read file')
      setUploadStatus('error')
    }
    reader.readAsDataURL(file)
  }
  
  const clearResumeFile = () => {
    setResumeFile(null)
    setResumeFileName(null)
    setUploadStatus('idle')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }
  
  const handleResumeMethodChange = (method: 'upload' | 'paste') => {
    // Clear previous data
    if (method === 'upload') {
      setInitialResume('')
      setResumeMethod('upload')
      // Trigger file dialog
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
      <p className="text-xs mt-1 text-gray-500">We'll extract the text automatically</p>
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
                      PDF uploaded successfully. Text will be extracted.
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
                    <p className="text-sm font-medium text-red-700">
                      Upload failed
                    </p>
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
              ) : uploadStatus === 'uploading' ? (
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    <Loader2 className="h-8 w-8 text-emerald-500 animate-spin" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      Processing file...
                    </p>
                    <p className="text-xs text-gray-500">
                      This may take a moment
                    </p>
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
        initialResume,
        resumeFile || undefined
      )
      
      if (result) {
        setError(null)
        // Clear signup form
        setSignupUsername('')
        setSignupPassword('')
        setSignupEmail('')
        setInitialResume('')
        setResumeFile(null)
        setResumeFileName(null)
        setResumeMethod('none')
        setUploadStatus('idle')
        
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
        )}
      </DialogContent>
    </Dialog>
  )
} 