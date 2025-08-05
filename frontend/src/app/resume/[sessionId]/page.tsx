"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Loader2, Download, ArrowLeft, CheckCircle, FileText, Share2, User, Mail, Star, Clock, Zap, Shield } from "lucide-react"
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
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Loading your resume...</h2>
          <p className="text-gray-600">Please wait while we prepare your tailored resume</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FileText className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Resume Not Found</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <Button 
            onClick={handleBackToHome}
            className="bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={handleBackToHome}
                className="text-gray-600 hover:text-gray-800"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <div className="h-6 w-px bg-gray-300" />
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="font-medium text-gray-800">Resume Generated Successfully!</span>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleDownload}
                disabled={isDownloading}
                className="bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 font-medium shadow-sm hover:shadow-md"
              >
                {isDownloading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Download PDF
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Prominent CTA Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-violet-600 to-purple-600 relative overflow-hidden">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">

            <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
              🎉 Your Tailored ATS-Optimized Resume is Ready!
            </h2>
            <p className="text-blue-100 text-lg mb-4 max-w-2xl mx-auto">
              Want to remove the watermark and create unlimited resumes? 
              <span className="font-semibold text-yellow-300"> Sign up now</span>
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <Button
                onClick={handleSignUp}
                size="lg"
                className="bg-white text-blue-600 hover:bg-gray-50 font-bold text-4xl px-16 py-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all transform hover:scale-105"
              >
                <Zap className="h-10 w-10 mr-4" />
                Get Full Access - FREE
              </Button>

            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* PDF Viewer - Much Larger */}
          <div className="lg:col-span-4">
            <div className="bg-white rounded-2xl shadow-2xl border border-white/20 overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-violet-600 px-6 py-4">
                <div className="flex items-center justify-between">
                  <h1 className="text-xl font-bold text-white flex items-center">
                    <FileText className="h-5 w-5 mr-2" />
                    Your Tailored Resume
                  </h1>
                  <div className="text-yellow-300 text-sm font-medium">
                    ⚡ ATS-Optimized & Job-Specific
                  </div>
                </div>
              </div>
              <div className="p-2">
                {pdfUrl && !pdfIframeError && (
                  <iframe
                    src={pdfUrl}
                    className="w-full border-0 rounded-lg"
                    style={{ height: '1000px' }}
                    title="Resume Preview"
                    onError={handlePdfIframeError}
                    onLoad={(e) => {
                      // Check if iframe content loaded successfully
                      const iframe = e.target as HTMLIFrameElement
                      try {
                        // If we can't access the content or if it's empty, show fallback
                        setTimeout(() => {
                          if (!iframe.contentDocument || iframe.contentDocument.body?.children.length === 0) {
                            handlePdfIframeError()
                          }
                        }, 2000)
                      } catch {
                        // Cross-origin error means the PDF might be loading, so we'll let it be
                      }
                    }}
                  />
                )}
                {pdfUrl && pdfIframeError && (
                  <div className="h-[1000px] flex flex-col items-center justify-center p-8 bg-gray-50 rounded-lg">
                    <div className="text-center space-y-4 max-w-md">
                      <div className="w-20 h-20 bg-red-100 rounded-2xl flex items-center justify-center mx-auto">
                        <FileText className="w-10 h-10 text-red-600" />
                      </div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        PDF Preview Not Available
                      </h3>
                      <p className="text-gray-600">
                        Your browser's PDF viewer needs to be enabled for inline preview.
                      </p>
                      <PdfViewerGuidance className="mt-4" />
                      <Button
                        onClick={handleDownload}
                        className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white"
                        disabled={isDownloading}
                      >
                        {isDownloading ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Downloading...
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4 mr-2" />
                            Download Resume
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
          <div className="lg:col-span-1 space-y-4">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-lg border border-white/20 p-4">
              <h3 className="text-lg font-bold text-gray-800 mb-3">Quick Actions</h3>
              <div className="space-y-3">
                <Button
                  onClick={handleDownload}
                  disabled={isDownloading}
                  className="w-full bg-white hover:bg-gray-50 text-gray-900 border border-gray-300 font-medium shadow-sm hover:shadow-md"
                >
                  {isDownloading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  Download PDF
                </Button>
                <Button
                  onClick={handleSignUp}
                  className="w-full bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-700 hover:to-violet-700 text-white"
                >
                  <User className="h-4 w-4 mr-2" />
                  Remove Watermark
                </Button>
              </div>
            </div>

            {/* Benefits */}
            <div className="bg-white rounded-xl shadow-lg border border-white/20 p-4">
              <h3 className="text-lg font-bold text-gray-800 mb-3">Why Sign Up?</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Remove watermarks forever</span>
                </div>
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Unlimited resume generation</span>
                </div>
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Save & organize resumes</span>
                </div>
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Track job applications</span>
                </div>
                <div className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Cover letter generation</span>
                </div>
              </div>
            </div>


          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-8 bg-gradient-to-r from-violet-600 to-purple-600 rounded-2xl shadow-2xl p-8 text-center text-white">
          <h2 className="text-2xl font-bold mb-3">Ready to Land Your Dream Job?</h2>
          <p className="text-violet-100 mb-6 max-w-2xl mx-auto">
            Join thousands of professionals who've boosted their interview rates with Zumud. 
            Remove the watermark and unlock unlimited resume generation today.
          </p>
          <Button
            onClick={handleSignUp}
            size="lg"
            className="bg-white text-violet-600 hover:bg-gray-50 font-bold text-xl px-12 py-4 rounded-xl shadow-xl hover:shadow-2xl transition-all transform hover:scale-105"
          >
            <Mail className="h-6 w-6 mr-3" />
            Start Free Account - 30 Seconds
          </Button>
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