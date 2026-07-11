"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, Upload, CheckCircle, ArrowLeft, Save, LogIn } from "lucide-react"
import { resume } from "@/lib/api"
import Link from "next/link"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { errorMessage, signOut } from "@/lib/utils"
import { useRouter } from "next/navigation"

export default function ProfileSettingsPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAuthError, setIsAuthError] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [resumeData, setResumeData] = useState<string>("")
  
  // Resume upload states
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Function to redirect to login page
  const redirectToLogin = async () => {
    await signOut()
    // Redirect to home/login page
    router.push('/')
  }

  const fetchResumeData = async () => {
    try {
      const data = await resume.getResume()
      if (data && data.resume_content) {
        setResumeData(data.resume_content)
      }
      setIsAuthError(false)
    } catch (err) {
      console.error('Failed to load resume:', err)
      const message = errorMessage(err)
      
      // Check if this is an authentication error
      if (message && (
          message.includes('session has expired') || 
          message.includes('login') || 
          message.includes('token') || 
          message.includes('unauthorized') ||
          message.includes('authentication')
      )) {
        // Show authentication error message
        setError('Your session has expired. Please log in again to continue.')
        setIsAuthError(true)
      } else {
        // For other errors, show the appropriate message
        setError(message || 'Failed to load your current resume. Please try again later.')
        setIsAuthError(false)
      }
    }
  }

  // Load current resume data
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: all setState here runs after awaits
    fetchResumeData()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount
  }, [])

  const handleUpdateResume = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    setIsAuthError(false)

    try {
      await resume.updateResume(resumeData)
      setSuccess('Resume text updated successfully!')
    } catch (err) {
      const message = errorMessage(err)
      // Check if this is an authentication error
      if (message && (
          message.includes('session has expired') || 
          message.includes('login') || 
          message.includes('token') || 
          message.includes('unauthorized') ||
          message.includes('authentication')
      )) {
        // Show authentication error message
        setError('Your session has expired. Please log in again to continue.')
        setIsAuthError(true)
      } else {
        setError(message || 'Failed to update resume text')
        setIsAuthError(false)
      }
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    // Reset upload status
    setUploadStatus('idle')
    setError(null)
    setIsAuthError(false)
    
    // Check if the file is a PDF
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file')
      return
    }
    
    // Check if the file is too large (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size exceeds 5MB limit')
      return
    }
    
    setResumeFile(file)
  }
  
  const handleUploadResume = async () => {
    if (!resumeFile) {
      setError('Please select a PDF file first')
      return
    }
    
    setUploadStatus('uploading')
    setError(null)
    setSuccess(null)
    setIsAuthError(false)
    
    try {
      await resume.uploadResumePdf(resumeFile)
      setUploadStatus('success')
      setSuccess('Resume uploaded successfully!')
      
      // Refresh resume data after upload
      await fetchResumeData()
      
      // Clear the file input after successful upload
      setTimeout(() => {
        setResumeFile(null)
        setUploadStatus('idle')
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }, 3000)
    } catch (err) {
      const message = errorMessage(err)
      // Check if this is an authentication error
      if (message && (
          message.includes('session has expired') || 
          message.includes('login') || 
          message.includes('token') || 
          message.includes('unauthorized') ||
          message.includes('authentication')
      )) {
        // Show authentication error message
        setUploadStatus('error')
        setError('Your session has expired. Please log in again to continue.')
        setIsAuthError(true)
      } else {
        setUploadStatus('error')
        setError(message || 'Failed to upload resume')
        setIsAuthError(false)
      }
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container-page max-w-3xl py-8 md:py-12">
        <div className="mb-8 flex items-center gap-3">
          <Link href="/dashboard" aria-label="Back to dashboard">
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">Profile settings</h1>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
            <div className="flex items-start justify-between gap-4">
              <span className="block sm:inline">{error}</span>
              {isAuthError && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={redirectToLogin}
                  className="shrink-0"
                >
                  <LogIn className="h-4 w-4 mr-2" />
                  Log in
                </Button>
              )}
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/10 px-4 py-3 text-sm text-[var(--success)]" role="alert">
            <span className="block sm:inline">{success}</span>
          </div>
        )}

        <div className="surface mb-6 p-6">
          <h2 className="text-xl font-semibold">Manage your resume</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Edit your resume text directly or upload a new PDF resume.
          </p>

          <Tabs defaultValue="edit" className="mt-5">
            <TabsList className="mb-4 w-full">
              <TabsTrigger value="edit" className="flex-1">Edit resume text</TabsTrigger>
              <TabsTrigger value="upload" className="flex-1">Upload PDF resume</TabsTrigger>
            </TabsList>

            <TabsContent value="edit" className="space-y-4">
              <textarea
                value={resumeData}
                onChange={(e) => setResumeData(e.target.value)}
                className="field h-96 resize-none"
                placeholder="Your resume content here..."
              />

              <div className="flex justify-end">
                <Button onClick={handleUpdateResume} variant="brand" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save resume
                    </>
                  )}
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="upload" className="space-y-4">
              <div className="rounded-xl border border-border">
                <div className="p-4">
                  {uploadStatus === 'success' ? (
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-8 w-8 shrink-0 text-[var(--success)]" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">{resumeFile?.name}</p>
                        <p className="text-sm text-[var(--success)]">Resume uploaded successfully!</p>
                      </div>
                    </div>
                  ) : uploadStatus === 'uploading' ? (
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-8 w-8 shrink-0 animate-spin text-brand" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">Processing resume...</p>
                        <p className="text-sm text-muted-foreground">This may take a moment</p>
                      </div>
                    </div>
                  ) : (
                    <div className="py-8 text-center">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="application/pdf"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                      <button
                        type="button"
                        className="mx-auto mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-brand/10 text-brand transition-colors hover:bg-brand/20"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="h-8 w-8" />
                      </button>
                      <p className="text-sm">
                        <button
                          type="button"
                          className="font-medium text-brand hover:underline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Click to upload
                        </button>{" "}
                        or drag and drop
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">PDF up to 5MB</p>

                      {resumeFile && (
                        <div className="mt-3">
                          <p className="text-sm font-medium">{resumeFile.name}</p>
                          <Button
                            type="button"
                            onClick={handleUploadResume}
                            variant="brand"
                            className="mt-2"
                            size="sm"
                          >
                            Upload resume
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="text-sm text-muted-foreground">
                <p>When you upload a new resume, we&apos;ll automatically extract the text content for you.</p>
                <p>This will replace your current resume text.</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <div className="surface p-6">
          <h2 className="text-xl font-semibold">Account settings</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Additional settings for your account will appear here.
          </p>

          <div className="mt-4 rounded-xl border border-dashed border-border bg-muted/40 p-6 text-center">
            <p className="text-sm text-muted-foreground">Additional account settings coming soon</p>
          </div>
        </div>
      </div>
    </div>
  )
} 