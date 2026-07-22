"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { errorMessage, signOut } from "@/lib/utils"
import { createClient } from "@/lib/supabase/client"
import { applications, preferences, billing } from "@/lib/api"
import PdfViewer from "@/components/pdf-viewer"
import PreferencesPrompt from "@/components/ui/preferences-prompt"
import InlineResumeProgress from "@/components/ui/inline-resume-progress"
import Sidebar from "@/components/ui/sidebar"
import { 
  Download, 
  Loader2, 
  FileCode, 
  ExternalLink, 
  AlertCircle, 
  MessageSquare, 
  Copy as CopyIcon, 
  LogIn,
  FileText,
  Mail,
  HelpCircle,
  Send,
  Sparkles,
  CreditCard
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function Dashboard() {
  const router = useRouter()
  const [userData, setUserData] = useState<{ first_name: string } | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [coverLetter, setCoverLetter] = useState("")
  const [isGeneratingResume, setIsGeneratingResume] = useState(false)
  const [showResumeProgress, setShowResumeProgress] = useState(false)
  const [forceCompleteProgress, setForceCompleteProgress] = useState(false)
  const [isGeneratingCoverLetter, setIsGeneratingCoverLetter] = useState(false)
  const [isGeneratingAnswer, setIsGeneratingAnswer] = useState(false)
  const [generatedResumePdf, setGeneratedResumePdf] = useState<string | null>(null)
  const [generatedResumeFilename, setGeneratedResumeFilename] = useState<string | null>(null)
  const [isDownloadingTeX, setIsDownloadingTeX] = useState(false)
  const [isDownloadingCoverLetter, setIsDownloadingCoverLetter] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAuthError, setIsAuthError] = useState(false)
  const [isPaymentError, setIsPaymentError] = useState(false)
  const [isLoadingPortal, setIsLoadingPortal] = useState(false)
  const [isPreparingOverleaf, setIsPreparingOverleaf] = useState(false)
  const [editInstruction, setEditInstruction] = useState("")
  const [isEditingResume, setIsEditingResume] = useState(false)
  const [updatedResumeJson, setUpdatedResumeJson] = useState<string | null>(null)
  const [lastGeneratedResumeJson, setLastGeneratedResumeJson] = useState<string | null>(null)
  const [coverLetterEditInstruction, setCoverLetterEditInstruction] = useState('')
  const [isEditingCoverLetter, setIsEditingCoverLetter] = useState(false)
  const [downloadCoverLetterUrl, setDownloadCoverLetterUrl] = useState<string | null>(null)
  const [downloadCoverLetterFilename, setDownloadCoverLetterFilename] = useState<string | null>(null)
  const [answerEditInstruction, setAnswerEditInstruction] = useState('')
  const [isEditingAnswer, setIsEditingAnswer] = useState(false)
  const [activeTab, setActiveTab] = useState<'resume' | 'cover-letter' | 'question' | null>(null)
  const [followUpInstruction, setFollowUpInstruction] = useState('')
  
  // Preferences prompt state
  const [showPreferencesPrompt, setShowPreferencesPrompt] = useState(false)
  const [currentEditInstruction, setCurrentEditInstruction] = useState("")

  // State to provide feedback after copying the cover letter (optional future use)
  const [isCoverLetterCopied, setIsCoverLetterCopied] = useState(false)
  const [isAnswerCopied, setIsAnswerCopied] = useState(false)

    // Ref for the main input area to scroll to
  const inputAreaRef = useRef<HTMLDivElement>(null)
  
  // State to track if user has made their first generation
  const [hasGenerated, setHasGenerated] = useState(false)
  
  // State for simple application session management (implicit)
  const [isNewApplication, setIsNewApplication] = useState(false)

 

  // Load user data on mount from the Supabase session.
  useEffect(() => {
    let active = true
    const supabase = createClient()
    supabase.auth.getUser().then(({ data }) => {
      if (active && data.user) {
        setUserData({ first_name: deriveFirstName(data.user) })
      }
    })
    return () => {
      active = false
    }
  }, [])

  // Set new application flag when job description changes (implicit intent detection)
  useEffect(() => {
    if (jobDescription.trim()) {
      // Job description changed, so next generation should be a new application
      // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: derive instead of mirroring state
      setIsNewApplication(true)
    } else {
      setIsNewApplication(false)
    }
  }, [jobDescription])



  const handleLogout = async () => {
    await signOut()
    window.location.reload()
  }

  // Function to redirect to login page
  const redirectToLogin = async () => {
    await signOut()
    // Redirect to home/login page
    router.push('/')
  }

  // Handle payment method portal
  const handleAddPaymentMethod = async () => {
    try {
      setIsLoadingPortal(true)
      const response = await billing.createCustomerPortalSession()
      
      if (response && response.portal_url) {
        // Redirect to Stripe Customer Portal payment methods page directly
        const paymentMethodsUrl = `${response.portal_url}/payment-methods`
        window.location.href = paymentMethodsUrl
      } else {
        console.error('No portal URL received from API')
        alert('Unable to open billing portal. Please try again.')
      }
    } catch (error) {
      console.error('Failed to create customer portal session:', error)
      alert('Unable to open billing portal. Please try again.')
    } finally {
      setIsLoadingPortal(false)
    }
  }

  // Reusable function to handle errors, especially timeouts
  const handleError = (err: unknown, defaultMessage: string) => {
    console.error(defaultMessage, err)
    const message = errorMessage(err)
    
    // Check if this is a payment method error
    if (message && (
        message.includes('payment method') || 
        message.includes('add a payment') ||
        message.includes('current balance') ||
        message.includes('€') ||
        message.includes('402')
    )) {
      // Show payment error message with add payment method option
      setError(message)
      setIsPaymentError(true)
      setIsAuthError(false)
    } else if (message && (
        message.includes('session has expired') || 
        message.includes('login') || 
        message.includes('token') || 
        message.includes('unauthorized') ||
        message.includes('authentication')
    )) {
      // Show authentication error message with login option
      setError('Your session has expired. Please log in again to continue.')
      setIsAuthError(true)
      setIsPaymentError(false)
    } else if ((err instanceof Error && err.name === 'AbortError') || message.includes("took too long to complete")) {
      setError("Timeout: The request took too long to complete. Try again with a shorter job description.")
      setIsAuthError(false)
      setIsPaymentError(false)
    } else if (message && (
      message.includes("414") || 
      message.includes("Request-URI Too Large") || 
      message.includes("too large") ||
      message.toLowerCase().includes("request too large")
    )) {
      setError("The job description you provided is too long to process. Please try shortening it.")
      setIsAuthError(false)
      setIsPaymentError(false)
    } else {
      setError(message || defaultMessage)
      setIsAuthError(false)
      setIsPaymentError(false)
    }
  }

  // Creates a URL from a blob and triggers download
  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    // Release the URL after a short delay
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    return url
  }

  // Generic async operation handler with processing message
  const asyncOperation = async <T,>(
    operation: () => Promise<T>,
    setLoading: (loading: boolean) => void,
    operationName: string,
    processingMessage: string,
    onSuccess: (result: T) => void,
    defaultErrorMessage: string,
    validationFn?: () => string | null
  ) => {
    // Run validation if provided
    if (validationFn) {
      const validationError = validationFn()
      if (validationError) {
        setError(validationError)
        setIsAuthError(false)
        return
      }
    }

    setLoading(true)
    setError(null)
    setIsAuthError(false)
    
    try {
      const result = await operation()
      setError(null)
      setIsAuthError(false)
      onSuccess(result)
    } catch (err) {
      // Hide progress immediately on any error for resume generation
      if (operationName === "resume generation") {
        setShowResumeProgress(false)
        setForceCompleteProgress(false)
      }
      

      
      handleError(err, defaultErrorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateResume = () => {
    setActiveTab('resume')
    // Clear previous resume immediately for better UX
    setGeneratedResumePdf(null)
    setGeneratedResumeFilename(null)
    // Show inline progress (not blocking modal)
    setShowResumeProgress(true)
    setForceCompleteProgress(false) // Reset force complete flag
    // Mark as first generation to hide welcome section
    setHasGenerated(true)
    
    asyncOperation(
      // Operation to perform
      async () => {
        // Generate the resume PDF first
        const pdfResult = await applications.generateResume(jobDescription, isNewApplication)
        
        // After generating the PDF, fetch the latest resume JSON
        try {
          const jsonResult = await applications.getLatestResumeJson()
          if (jsonResult && jsonResult.resume_json) {
            setLastGeneratedResumeJson(jsonResult.resume_json)
          }
        } catch (err) {
          console.error("Error fetching resume JSON:", err)
          // Continue with the PDF generation even if JSON fetch fails
        }
        
        return pdfResult
      },
      // Set loading state
      setIsGeneratingResume,
      // Operation name 
      "resume generation",
      // Processing message
      "Generating resume...",
      // Success handler
      (result) => {
        // Handle new response format with blob and filename
        const blob = result.blob || result; // fallback to result if it's just a blob
        const filename = result.filename || null;
        
        const pdfUrl = URL.createObjectURL(blob)
        setGeneratedResumePdf(pdfUrl)
        setGeneratedResumeFilename(filename)
        
        // Trigger progress completion animation
        setForceCompleteProgress(true)
        
        // Reset new application flag after successful generation
        setIsNewApplication(false)
      },
      // Default error message
      "Failed to generate resume",
      // Validation
      () => !jobDescription.trim() ? "Please enter a job description" : null
    )
  }

  const handleResumeProgressComplete = () => {
    // This will be called when progress animation completes
    setShowResumeProgress(false)
    setForceCompleteProgress(false)
  }

  const handleGenerateCoverLetter = () => {
    setActiveTab('cover-letter')
    // Clear previous cover letter immediately for better UX
    setCoverLetter('')
    setDownloadCoverLetterUrl(null)
    setDownloadCoverLetterFilename(null)
    // Mark as first generation to hide welcome section
    setHasGenerated(true)
    asyncOperation(
      () => applications.generateCoverLetter(jobDescription, isNewApplication),
      setIsGeneratingCoverLetter,
      "cover letter generation",
      "Generating cover letter...",
      (result) => {
        setCoverLetter(result)
        // Reset new application flag after successful generation
        setIsNewApplication(false)
      },
      "Failed to generate cover letter",
      () => !jobDescription.trim() ? "Please enter a job description" : null
    )
  }

  const handleAnswerQuestion = () => {
    setActiveTab('question')
    // Clear previous answer immediately for better UX
    setAnswer('')
    // Mark as first generation to hide welcome section
    setHasGenerated(true)
    asyncOperation(
      () => applications.answerQuestion(jobDescription, question, isNewApplication),
      setIsGeneratingAnswer,
      "answer generation",
      "Generating answer...",
      (result) => {
        setAnswer(result)
        // Reset new application flag after successful generation
        setIsNewApplication(false)
      },
      "Failed to generate answer",
      () => {
        if (!jobDescription.trim()) return "Please enter a job description"
        if (!question.trim()) return "Please enter a question"
        return null
      }
    )
  }

  const handleFollowUpSubmit = () => {
    if (!followUpInstruction.trim()) return

    if (activeTab === 'resume') {
      handleEditResume(followUpInstruction)
    } else if (activeTab === 'cover-letter') {
      handleEditCoverLetter(followUpInstruction)
    } else if (activeTab === 'question') {
      handleEditAnswer(followUpInstruction)
    }
    
    setFollowUpInstruction('')
  }

  // Helper function for quick actions
  const handleQuickAction = (instruction: string) => {
    if (activeTab === 'resume') {
      handleEditResume(instruction)
    } else if (activeTab === 'cover-letter') {
      handleEditCoverLetter(instruction)
    } else if (activeTab === 'question') {
      handleEditAnswer(instruction)
    }
  }



  const handleDownloadResume = async () => {
    if (generatedResumePdf) {
      const link = document.createElement("a")
      link.href = generatedResumePdf
      link.download = generatedResumeFilename || "resume.pdf"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleDownloadTeX = () => {
    asyncOperation(
      () => applications.getResumeTeX(),
      setIsDownloadingTeX,
      "TeX download",
      "Downloading TeX...",
      (blob) => downloadBlob(blob, "resume.tex"),
      "Failed to download TeX file"
    )
  }

  const handleOpenInOverleaf = () => {
    asyncOperation(
      () => applications.getResumeTeXContent(),
      setIsPreparingOverleaf,
      "Overleaf preparation",
      "Preparing Overleaf...",
      (texContent) => {
        // Create a form to POST to Overleaf
        const form = document.createElement('form')
        form.method = 'post'
        form.action = 'https://www.overleaf.com/docs'
        form.target = '_blank'
        form.style.display = 'none'

        // Create an input field with the content
        const input = document.createElement('input')
        input.type = 'hidden'
        input.name = 'snip'
        input.value = texContent

        // Add input to form and submit
        form.appendChild(input)
        document.body.appendChild(form)
        form.submit()
        document.body.removeChild(form)
      },
      "Failed to edit in Overleaf"
    )
  }

  const handleDownloadCoverLetter = () => {
    asyncOperation(
      () => applications.getCoverLetterPDF(),
      setIsDownloadingCoverLetter,
      "cover letter download",
      "Downloading cover letter...",
      (result) => {
        const blob = result.blob || result
        const filename = result.filename || "cover_letter.pdf"
        const url = downloadBlob(blob, filename)
        setDownloadCoverLetterUrl(url)
        setDownloadCoverLetterFilename(filename)
      },
      "Failed to download cover letter"
    )
  }

  const handleCopyCoverLetter = () => {
    if (coverLetter) {
      navigator.clipboard.writeText(coverLetter)
      setIsCoverLetterCopied(true)
      setTimeout(() => setIsCoverLetterCopied(false), 2000)
    }
  }

  const handleCopyAnswer = () => {
    if (answer) {
      navigator.clipboard.writeText(answer)
      setIsAnswerCopied(true)
      setTimeout(() => setIsAnswerCopied(false), 2000)
    }
  }

  const handleEditResume = (instruction?: string) => {
    const instructionToUse = instruction || editInstruction
    asyncOperation(
      () => applications.editResumeWithInstructions(instructionToUse, jobDescription),
      setIsEditingResume,
      "resume editing",
      "Editing resume...",
      (result) => {
        const blob = result.blob || result
        const filename = result.filename || null
        
        const pdfUrl = URL.createObjectURL(blob)
        setGeneratedResumePdf(pdfUrl)
        setGeneratedResumeFilename(filename)
        
        if (result.updated_json) {
          setLastGeneratedResumeJson(result.updated_json)
        }
        
        setEditInstruction("")
      },
      "Failed to edit resume",
      () => !instructionToUse.trim() ? "Please enter an edit instruction" : null
    )
  }

  const handleEditCoverLetter = (instruction?: string) => {
    const instructionToUse = instruction || coverLetterEditInstruction
    asyncOperation(
      () => applications.editCoverLetterWithInstructions(instructionToUse, jobDescription),
      setIsEditingCoverLetter,
      "cover letter editing",
      "Editing cover letter...",
      async (result) => {
        // Handle new response format with blob and filename for cover letters
        const blob = result.blob || result
        const filename = result.filename || null
        
        // Create a URL for the PDF
        const pdfUrl = URL.createObjectURL(blob)
        setDownloadCoverLetterUrl(pdfUrl)
        setDownloadCoverLetterFilename(filename)
        
        // Fetch the updated cover letter text
        try {
          const updatedText = await applications.getCoverLetterText()
          if (updatedText) {
            setCoverLetter(updatedText)
          }
        } catch (err) {
          console.error("Error fetching updated cover letter text:", err)
        }
        
        setCoverLetterEditInstruction('')
      },
      "Failed to edit cover letter",
      () => !instructionToUse.trim() ? "Please enter an edit instruction" : null
    )
  }

  const handleEditAnswer = (instruction?: string) => {
    const instructionToUse = instruction || answerEditInstruction
    asyncOperation(
      () => applications.editAnswerWithInstructions(instructionToUse, answer, question, jobDescription),
      setIsEditingAnswer,
      "answer editing",
      "Editing answer...",
      (result) => {
        if (result) {
          setAnswer(result)
        }
        setAnswerEditInstruction('')
      },
      "Failed to edit answer",
      () => !instructionToUse.trim() ? "Please enter an edit instruction" : null
    )
  }

  const handleSavePreference = async (preference: string) => {
    try {
      await preferences.addUserPreference(preference)
      setShowPreferencesPrompt(false)
    } catch (err) {
      console.error("Error saving preference:", err)
    }
  }

  const handleDismissPreferencesPrompt = () => {
    setShowPreferencesPrompt(false)
  }

  return (
    <div className="ambient-glow relative min-h-screen bg-background pb-40 md:pb-12">
      {/* Sidebar */}
      <Sidebar onLogout={handleLogout} />

      {/* Main Content */}
      <div className="relative">
        {/* Main Content Area */}
        <div className="mx-auto max-w-4xl px-4 py-8 md:px-8 md:py-12">
          {/* Header - hide after first generation */}
          {!hasGenerated && (
            <div className="text-center mb-8 md:mb-12 transition-all duration-500 ease-out">
              <h1 className="mb-2 text-2xl font-bold tracking-tight text-brand-gradient md:text-3xl lg:text-4xl">
                {userData?.first_name ? `Good ${getGreeting()}, ${userData.first_name}` : "Welcome back"}
              </h1>
              <p className="text-sm text-muted-foreground md:text-base">
                Ready to create a tailored document for your next opportunity?
              </p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {isAuthError && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={redirectToLogin}
                        className="text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600 dark:hover:bg-red-900/30"
                      >
                        <LogIn className="h-4 w-4 mr-2" />
                        Log in again
                      </Button>
                    )}
                    {isPaymentError && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleAddPaymentMethod}
                        disabled={isLoadingPortal}
                        className="text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-600 dark:hover:bg-red-900/30 font-medium"
                      >
                        {isLoadingPortal ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Opening...
                          </>
                        ) : (
                          <>
                            <CreditCard className="h-4 w-4 mr-2" />
                            Add Payment Method
                          </>
                        )}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Main Input Area */}
          <div ref={inputAreaRef} className="surface mb-8 p-4 shadow-lg shadow-brand/5 md:p-6 lg:p-8">
            <div className="space-y-6">
              {/* Job Description Input */}
              <div>
                <label className="mb-3 block text-sm font-semibold">
                  Job Description
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here to instantly generate a tailored document..."
                  rows={6}
                  className="field resize-none"
                />
              </div>

              {/* Action Buttons - Improved mobile layout */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
                <Button
                  onClick={handleGenerateResume}
                  variant="brand"
                  disabled={isGeneratingResume || !jobDescription.trim()}
                  className="h-12 text-sm font-semibold md:h-14 md:text-base"
                >
                  {isGeneratingResume ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      <span className="hidden sm:inline">Generating...</span>
                      <span className="sm:hidden">Gen...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      <span className="hidden sm:inline">Generate Resume</span>
                      <span className="sm:hidden">Resume</span>
                    </>
                  )}
                </Button>

                <Button
                  onClick={handleGenerateCoverLetter}
                  disabled={isGeneratingCoverLetter || !jobDescription.trim()}
                  className="h-12 rounded-lg bg-[var(--accent2)] text-sm font-semibold text-white transition-all duration-200 hover:brightness-110 hover:shadow-lg disabled:opacity-50 md:h-14 md:text-base"
                >
                  {isGeneratingCoverLetter ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      <span className="hidden sm:inline">Generating...</span>
                      <span className="sm:hidden">Gen...</span>
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      <span className="hidden sm:inline">Generate Cover Letter</span>
                      <span className="sm:hidden">Cover Letter</span>
                    </>
                  )}
                </Button>

                <Button
                  onClick={() => setActiveTab('question')}
                  variant="outline"
                  disabled={isGeneratingAnswer || !jobDescription.trim()}
                  className="h-12 text-sm font-semibold md:h-14 md:text-base sm:col-span-2 lg:col-span-1"
                >
                  <HelpCircle className="mr-2 h-4 w-4 text-brand" />
                  <span className="hidden sm:inline">Answer Question</span>
                  <span className="sm:hidden">Question</span>
                </Button>
              </div>

              {/* Resume Progress - Inline */}
              {showResumeProgress && (
                <div className="pt-4 border-t border-border">
                  <InlineResumeProgress 
                    isVisible={showResumeProgress}
                    forceComplete={forceCompleteProgress}
                    onComplete={handleResumeProgressComplete}
                  />
                </div>
              )}

              {/* Question Input (shown when Answer Question is selected) */}
              {activeTab === 'question' && (
                <div className="space-y-4 pt-4 border-t border-border">
                  <label className="block text-sm font-semibold">
                    Application Question
                  </label>
                  <div className="relative">
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Enter the application question you need to answer..."
                      rows={3}
                      className="field resize-none pr-4 md:pr-24"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          if (!isGeneratingAnswer && jobDescription.trim() && question.trim()) {
                            handleAnswerQuestion()
                          }
                        }
                      }}
                    />
                    <div className="hidden md:flex absolute right-3 top-3 items-center gap-1 text-xs text-muted-foreground">
                      <kbd className="flex items-center gap-1 rounded border border-border bg-muted px-2 py-1 font-mono text-xs">
                        <span>Enter</span>
                        <span>↵</span>
                      </kbd>
                      <span>to generate</span>
                    </div>
                  </div>
                  <Button
                    onClick={handleAnswerQuestion}
                    variant="brand"
                    disabled={isGeneratingAnswer || !jobDescription.trim() || !question.trim()}
                    className="w-full font-semibold sm:w-auto"
                  >
                    {isGeneratingAnswer ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating Answer...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate Your Tailored Answer
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* Results Section */}
          {(generatedResumePdf || coverLetter || answer) && (
            <div className="space-y-6">
              {/* Resume Results */}
              {generatedResumePdf && activeTab === 'resume' && (
                <div className="surface p-4 md:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                    <h3 className="text-lg font-semibold">
                      Your Tailored Resume
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={handleDownloadResume}
                        variant="outline"
                        size="sm"
                        className="text-xs md:text-sm"
                      >
                        <Download className="h-4 w-4 mr-1 md:mr-2 text-brand" />
                        <span className="hidden sm:inline">Download </span>PDF
                      </Button>
                      <Button
                        onClick={handleDownloadTeX}
                        disabled={isDownloadingTeX}
                        variant="outline"
                        size="sm"
                        className="text-xs md:text-sm"
                      >
                        {isDownloadingTeX ? (
                          <Loader2 className="h-4 w-4 mr-1 md:mr-2 animate-spin" />
                        ) : (
                          <FileCode className="h-4 w-4 mr-1 md:mr-2 text-[var(--success)]" />
                        )}
                        <span className="hidden sm:inline">Download </span>TeX
                      </Button>
                      <Button
                        onClick={handleOpenInOverleaf}
                        disabled={isPreparingOverleaf}
                        variant="outline"
                        size="sm"
                        className="text-xs md:text-sm"
                      >
                        {isPreparingOverleaf ? (
                          <Loader2 className="h-4 w-4 mr-1 md:mr-2 animate-spin" />
                        ) : (
                          <ExternalLink className="h-4 w-4 mr-1 md:mr-2 text-[#e85d2c] dark:text-[#ff8a5e]" />
                        )}
                        <span className="hidden lg:inline">Edit in </span>Overleaf
                      </Button>
                    </div>
                  </div>
                  <div className="overflow-hidden rounded-xl border border-border">
                    <PdfViewer pdfUrl={generatedResumePdf} />
                  </div>
                </div>
              )}

              {/* Cover Letter Results */}
              {coverLetter && activeTab === 'cover-letter' && (
                <div className="surface p-4 md:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                    <h3 className="text-lg font-semibold">
                      Your Cover Letter
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        onClick={handleCopyCoverLetter}
                        variant="outline"
                        size="sm"
                        className="text-xs md:text-sm"
                      >
                        <CopyIcon className="h-4 w-4 mr-1 md:mr-2 text-brand" />
                        {isCoverLetterCopied ? 'Copied!' : 'Copy'}
                      </Button>
                      <Button
                        onClick={handleDownloadCoverLetter}
                        disabled={isDownloadingCoverLetter}
                        variant="outline"
                        size="sm"
                        className="text-xs md:text-sm"
                      >
                        {isDownloadingCoverLetter ? (
                          <Loader2 className="h-4 w-4 mr-1 md:mr-2 animate-spin" />
                        ) : (
                          <Download className="h-4 w-4 mr-1 md:mr-2 text-[var(--success)]" />
                        )}
                        <span className="hidden sm:inline">Download </span>PDF
                      </Button>
                    </div>
                  </div>
                  <div className="rounded-xl bg-muted/60 p-4">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-foreground/90">
                      {coverLetter}
                    </pre>
                  </div>
                </div>
              )}

              {/* Answer Results */}
              {answer && activeTab === 'question' && (
                <div className="surface p-4 md:p-6">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
                    <h3 className="text-lg font-semibold">
                      Your Answer
                    </h3>
                    <Button
                      onClick={handleCopyAnswer}
                      variant="outline"
                      size="sm"
                      className="w-full text-xs sm:w-auto md:text-sm"
                    >
                      <CopyIcon className="h-4 w-4 mr-1 md:mr-2 text-brand" />
                      {isAnswerCopied ? 'Copied!' : 'Copy Answer'}
                    </Button>
                  </div>
                  <div className="rounded-xl bg-muted/60 p-4">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-foreground/90">
                      {answer}
                    </pre>
                  </div>
                </div>
              )}

              {/* Enhanced Mobile-Friendly Make it Better Section */}
              {((activeTab === 'resume' && generatedResumePdf) || 
                (activeTab === 'cover-letter' && coverLetter) || 
                (activeTab === 'question' && answer)) && (
                <div className="fixed bottom-0 left-0 right-0 p-4 z-40 animate-in slide-in-from-bottom-4 fade-in duration-500 md:bottom-6 md:left-1/2 md:-translate-x-1/2 md:w-full md:max-w-4xl md:px-8">
                  <div className="rounded-t-2xl border border-border bg-card/95 p-4 shadow-2xl backdrop-blur-2xl md:rounded-2xl">
                    {/* Mobile: Stack vertically, Desktop: Single line */}
                    <div className="space-y-3 md:space-y-0">
                      {/* Title and quick actions */}
                      <div className="flex flex-col md:flex-row md:items-center gap-3 md:mb-3">
                        <div className="flex items-center gap-2">
                          <MessageSquare className="h-5 w-5 text-brand" />
                          <h3 className="text-lg font-semibold">
                            Make it better
                          </h3>
                        </div>
                        
                        {/* Quick action buttons - wrap on mobile */}
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() => handleQuickAction("Make it shorter and more concise")}
                            disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                            className="cursor-pointer px-2.5 py-1 text-xs font-medium rounded-full bg-blue-500/10 hover:bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-200/50 dark:border-blue-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            ✂️ <span className="hidden sm:inline">Make </span>shorter
                          </button>
                          <button
                            onClick={() => handleQuickAction("Make the tone more formal and professional")}
                            disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                            className="cursor-pointer px-2.5 py-1 text-xs font-medium rounded-full bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-200/50 dark:border-purple-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            👔 <span className="hidden sm:inline">More </span>formal
                          </button>
                          <button
                            onClick={() => handleQuickAction("Make the tone more casual and approachable")}
                            disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                            className="cursor-pointer px-2.5 py-1 text-xs font-medium rounded-full bg-orange-500/10 hover:bg-orange-500/20 text-orange-700 dark:text-orange-300 border border-orange-200/50 dark:border-orange-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            😊 <span className="hidden sm:inline">More </span>casual
                          </button>
                          <button
                            onClick={() => handleQuickAction("Add more technical skills and keywords relevant to the job")}
                            disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                            className="cursor-pointer px-2.5 py-1 text-xs font-medium rounded-full bg-violet-500/10 hover:bg-violet-500/20 text-violet-700 dark:text-violet-300 border border-violet-200/50 dark:border-violet-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            🔑 <span className="hidden sm:inline">Add </span>keywords
                          </button>
                        </div>
                      </div>

                      {/* Custom Input - Stack vertically on mobile */}
                      <div className="flex flex-col md:flex-row gap-3">
                        <div className="flex-1 relative">
                          <input
                            type="text"
                            value={followUpInstruction}
                            onChange={(e) => setFollowUpInstruction(e.target.value)}
                            placeholder="Or describe what you want to improve..."
                            className="field h-12 pr-4 md:pr-16"
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') {
                                e.preventDefault()
                                handleFollowUpSubmit()
                              }
                            }}
                            disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                          />
                          <div className="hidden md:flex absolute right-3 top-1/2 -translate-y-1/2 items-center gap-1 text-xs text-muted-foreground">
                            <kbd className="flex items-center gap-1 rounded border border-border bg-muted px-2 py-1 font-mono text-xs">
                              <span>Enter</span>
                              <span>↵</span>
                            </kbd>
                            <span>to update</span>
                          </div>
                        </div>
                        <Button
                          type="button"
                          variant="brand"
                          onClick={handleFollowUpSubmit}
                          disabled={!followUpInstruction.trim() || isEditingResume || isEditingCoverLetter || isEditingAnswer}
                          className="h-12 w-full px-6 font-semibold md:w-auto"
                        >
                          {(isEditingResume || isEditingCoverLetter || isEditingAnswer) ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Updating...
                            </>
                          ) : (
                            <>
                              <Send className="mr-2 h-4 w-4" />
                              Update
                            </>
                          )}
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          



           {/* Preferences Prompt */}
           {showPreferencesPrompt && (
             <PreferencesPrompt
               isVisible={showPreferencesPrompt}
               onSavePreference={handleSavePreference}
               onDismiss={handleDismissPreferencesPrompt}
               editInstruction={currentEditInstruction}
             />
           )}
        </div>
      </div>
    </div>
  )
}

// Helper function to get greeting based on time of day
function getGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'morning'
  if (hour < 17) return 'afternoon'
  return 'evening'
}

// Derive a friendly first name from the Supabase user (Google provides a full
// name; otherwise fall back to the email local part).
function deriveFirstName(user: {
  email?: string | null
  user_metadata?: { full_name?: string; name?: string }
}): string {
  const meta = user.user_metadata ?? {}
  const fullName = meta.full_name || meta.name
  if (fullName && fullName.trim()) {
    return fullName.trim().split(/\s+/)[0]
  }
  if (user.email) {
    return String(user.email).split('@')[0]
  }
  return ''
} 
