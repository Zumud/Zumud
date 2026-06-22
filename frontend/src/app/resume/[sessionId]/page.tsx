"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Loader2, Download, ArrowLeft, CheckCircle, FileText, User, Mail, Zap } from "lucide-react"
import AuthModal from "@/components/auth/auth-modal"
import { applications } from "@/lib/api"
import { PdfViewerGuidance } from "@/components/ui/pdf-viewer-guidance"

export default function GeneratedResumePage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string
  
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [pdfIframeError, setPdfIframeError] = useState(false)

  useEffect(() => {
    const loadResumeData = async () => {
      if (process.env.NODE_ENV === 'development') {
        console.log('Loading resume data for session:', sessionId)
      }
      
      // First, try to get the PDF blob from sessionStorage (for immediate access)
      const storedPdfBlob = sessionStorage.getItem(`resume_pdf_${sessionId}`)
      
      if (storedPdfBlob) {
        if (process.env.NODE_ENV === 'development') {
          console.log('Found PDF data in sessionStorage')
        }
        try {
          // Convert base64 back to blob and create URL
          const byteCharacters = atob(storedPdfBlob)
          const byteNumbers = new Array(byteCharacters.length)
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i)
          }
          const byteArray = new Uint8Array(byteNumbers)
          const blob = new Blob([byteArray], { type: 'application/pdf' })
          const url = URL.createObjectURL(blob)
          setPdfUrl(url)
          setIsLoading(false)
          return
        } catch (err) {
          console.error("Error loading from sessionStorage:", err)
          // Fall through to server fetch
        }
      }
      
      // If sessionStorage doesn't have the data, fetch from server
      if (process.env.NODE_ENV === 'development') {
        console.log('SessionStorage empty, fetching from server...')
      }
      try {
        setIsLoading(true)
        const resumeData = await applications.getAnonymousResume(sessionId)
        
        if (process.env.NODE_ENV === 'development') {
          console.log('Successfully fetched resume data from server:', { 
            hasData: !!resumeData, 
            sessionId: resumeData?.session_id,
            hasPdfData: !!resumeData?.pdf_base64 
          })
        }
        
        // Convert base64 back to blob and create URL
        const byteCharacters = atob(resumeData.pdf_base64)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray], { type: 'application/pdf' })
        const url = URL.createObjectURL(blob)
        setPdfUrl(url)
        setIsLoading(false)
      } catch (err: any) {
        console.error("Error fetching resume from server:", err)
        if (process.env.NODE_ENV === 'development') {
          console.error("Error details:", {
            message: err.message,
            stack: err.stack,
            sessionId
          })
        }
        setError("Resume not found or expired. Please generate a new one.")
        setIsLoading(false)
      }
    }

    loadResumeData()

    // Cleanup URL on unmount
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl)
      }
    }
  }, [sessionId])

  const handleDownload = () => {
    if (!pdfUrl) return
    
    setIsDownloading(true)
    
    const link = document.createElement('a')
    link.href = pdfUrl
    link.download = `tailored_resume_${new Date().toISOString().split('T')[0]}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    setTimeout(() => setIsDownloading(false), 1000)
  }

  const handleSignUp = () => {
    setShowAuthModal(true)
  }

  const handleAuthSuccess = () => {
    setShowAuthModal(false)
    // Optionally redirect to dashboard or refresh the page
    router.push('/dashboard')
  }

  const handleBackToHome = () => {
    router.push('/')
  }

  const handlePdfIframeError = () => {
    setPdfIframeError(true)
  }

  if (isLoading) {
    return (
      <div className="ambient-glow relative flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="mx-auto mb-4 h-12 w-12 animate-spin text-brand" />
          <h2 className="mb-2 text-xl font-semibold">Loading your resume…</h2>
          <p className="text-muted-foreground">Please wait while we prepare your tailored resume</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="ambient-glow relative flex min-h-screen items-center justify-center bg-background">
        <div className="mx-auto max-w-md p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <FileText className="h-8 w-8 text-destructive" />
          </div>
          <h2 className="mb-2 text-xl font-semibold">Resume not found</h2>
          <p className="mb-6 text-muted-foreground">{error}</p>
          <Button onClick={handleBackToHome} variant="brand">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to home
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="ambient-glow relative min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 z-20 border-b border-border/60 bg-background/80 backdrop-blur-xl">
        <div className="container-page py-3">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <Button variant="ghost" onClick={handleBackToHome} className="shrink-0">
                <ArrowLeft className="h-4 w-4 sm:mr-2" />
                <span className="hidden sm:inline">Back to home</span>
              </Button>
              <div className="hidden h-6 w-px bg-border sm:block" />
              <div className="hidden items-center gap-2 sm:flex">
                <CheckCircle className="h-5 w-5 text-[var(--success)]" />
                <span className="font-medium">Resume generated successfully</span>
              </div>
            </div>
            <Button onClick={handleDownload} variant="outline" disabled={isDownloading}>
              {isDownloading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Download className="h-4 w-4 mr-2 text-brand" />
              )}
              <span className="hidden sm:inline">Download </span>PDF
            </Button>
          </div>
        </div>
      </div>

      {/* Prominent CTA Banner */}
      <div className="container-page pt-6">
        <div className="bg-brand-gradient relative overflow-hidden rounded-2xl px-6 py-8 text-center shadow-lg shadow-brand/20">
          <div
            className="pointer-events-none absolute inset-0 opacity-60"
            style={{
              background:
                "radial-gradient(24rem 24rem at 12% 0%, rgba(255,255,255,0.18), transparent 60%)",
            }}
            aria-hidden="true"
          />
          <div className="relative mx-auto max-w-2xl">
            <h2 className="mb-2 text-2xl font-bold text-white md:text-3xl">
              🎉 Your tailored, ATS-optimized resume is ready
            </h2>
            <p className="mb-6 text-white/85">
              Sign up free to remove the watermark and generate unlimited documents.
            </p>
            <Button
              onClick={handleSignUp}
              size="xl"
              className="bg-white font-semibold text-[var(--brand)] shadow-lg hover:bg-white/90"
            >
              <Zap className="size-5" />
              Get full access for free
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container-page py-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          {/* PDF Viewer */}
          <div className="lg:col-span-4">
            <div className="surface overflow-hidden">
              <div className="bg-brand-gradient px-6 py-4">
                <div className="flex items-center justify-between gap-3">
                  <h1 className="flex items-center text-lg font-bold text-white">
                    <FileText className="mr-2 h-5 w-5" />
                    Your tailored resume
                  </h1>
                  <div className="hidden text-sm font-medium text-white/90 sm:block">
                    ⚡ ATS-optimized &amp; job-specific
                  </div>
                </div>
              </div>
              <div className="bg-card p-2">
                {pdfUrl && !pdfIframeError && (
                  <iframe
                    src={pdfUrl}
                    className="w-full rounded-lg border-0"
                    style={{ height: "80vh", minHeight: "600px" }}
                    title="Resume Preview"
                    onError={handlePdfIframeError}
                    onLoad={(e) => {
                      const iframe = e.target as HTMLIFrameElement
                      try {
                        setTimeout(() => {
                          if (!iframe.contentDocument || iframe.contentDocument.body?.children.length === 0) {
                            handlePdfIframeError()
                          }
                        }, 2000)
                      } catch {
                        /* Cross-origin: assume the PDF is loading */
                      }
                    }}
                  />
                )}
                {pdfUrl && pdfIframeError && (
                  <div className="flex min-h-[600px] flex-col items-center justify-center rounded-lg bg-muted/50 p-8">
                    <div className="max-w-md space-y-4 text-center">
                      <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-2xl bg-destructive/10">
                        <FileText className="h-10 w-10 text-destructive" />
                      </div>
                      <h3 className="text-lg font-semibold">PDF preview not available</h3>
                      <p className="text-muted-foreground">
                        Your browser&apos;s PDF viewer needs to be enabled for inline preview.
                      </p>
                      <PdfViewerGuidance className="mt-4" />
                      <Button
                        onClick={handleDownload}
                        variant="brand"
                        className="mt-4 w-full"
                        disabled={isDownloading}
                      >
                        {isDownloading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Downloading…
                          </>
                        ) : (
                          <>
                            <Download className="mr-2 h-4 w-4" />
                            Download resume
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Compact Sidebar */}
          <div className="space-y-4 lg:col-span-1">
            <div className="surface p-4">
              <h3 className="mb-3 text-base font-semibold">Quick actions</h3>
              <div className="space-y-3">
                <Button
                  onClick={handleDownload}
                  variant="outline"
                  className="w-full"
                  disabled={isDownloading}
                >
                  {isDownloading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2 text-brand" />
                  )}
                  Download PDF
                </Button>
                <Button onClick={handleSignUp} variant="brand" className="w-full">
                  <User className="h-4 w-4 mr-2" />
                  Remove watermark
                </Button>
              </div>
            </div>

            <div className="surface p-4">
              <h3 className="mb-3 text-base font-semibold">Why sign up?</h3>
              <div className="space-y-3 text-sm">
                {[
                  "Remove watermarks forever",
                  "Unlimited resume generation",
                  "Save & organize resumes",
                  "Track job applications",
                  "Cover letter generation",
                ].map((benefit) => (
                  <div key={benefit} className="flex items-start gap-2">
                    <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-[var(--success)]" />
                    <span className="text-muted-foreground">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="bg-brand-gradient relative mt-8 overflow-hidden rounded-2xl p-8 text-center shadow-lg shadow-brand/20">
          <div className="relative mx-auto max-w-2xl">
            <h2 className="mb-3 text-2xl font-bold text-white">Ready to land your dream job?</h2>
            <p className="mb-6 text-white/85">
              Remove the watermark and unlock unlimited resumes, cover letters, and answers.
            </p>
            <Button
              onClick={handleSignUp}
              size="xl"
              className="bg-white font-semibold text-[var(--brand)] shadow-lg hover:bg-white/90"
            >
              <Mail className="size-5" />
              Create your free account
            </Button>
          </div>
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
        defaultTab="signup"
      />
    </div>
  )
} 