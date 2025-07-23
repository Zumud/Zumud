"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { getUserData, removeAccessToken, removeUserData } from "@/lib/utils"
import { applications, preferences } from "@/lib/api"
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
  Sparkles
} from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function Dashboard() {
  const router = useRouter()
  const [userData, setUserData] = useState<any>(null)
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

 

  // Load user data on mount
  useEffect(() => {
    const storedUserData = getUserData()
    if (storedUserData) {
      setUserData(storedUserData)
    }
  }, [])



  const handleLogout = () => {
    removeAccessToken()
    removeUserData()
    window.location.reload()
  }

  // Function to redirect to login page
  const redirectToLogin = () => {
    // Clear auth data
    removeAccessToken()
    removeUserData()
    // Redirect to home/login page
    router.push('/')
  }

  // Reusable function to handle errors, especially timeouts
  const handleError = (err: any, defaultMessage: string) => {
    console.error(defaultMessage, err)
    
    // Check if this is an authentication error
    if (err.message && (
        err.message.includes('session has expired') || 
        err.message.includes('login') || 
        err.message.includes('token') || 
        err.message.includes('unauthorized') ||
        err.message.includes('authentication')
    )) {
      // Show authentication error message with login option
      setError('Your session has expired. Please log in again to continue.')
      setIsAuthError(true)
    } else if (err.name === 'AbortError' || (err.message && err.message.includes("took too long to complete"))) {
      setError("Timeout: The request took too long to complete. Try again with a shorter job description.")
      setIsAuthError(false)
    } else if (err.message && (
      err.message.includes("414") || 
      err.message.includes("Request-URI Too Large") || 
      err.message.includes("too large") ||
      err.message.toLowerCase().includes("request too large")
    )) {
      setError("The job description you provided is too long to process. Please try shortening it.")
      setIsAuthError(false)
    } else {
      setError(err.message || defaultMessage)
      setIsAuthError(false)
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
  const asyncOperation = async (
    operation: () => Promise<any>,
    setLoading: (loading: boolean) => void,
    operationName: string,
    processingMessage: string,
    onSuccess: (result: any) => void,
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
    } catch (err: any) {
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
        const pdfResult = await applications.generateResume(jobDescription)
        
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
      () => applications.generateCoverLetter(jobDescription),
      setIsGeneratingCoverLetter,
      "cover letter generation",
      "Generating cover letter...",
      (result) => setCoverLetter(result),
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
      () => applications.answerQuestion(jobDescription, question),
      setIsGeneratingAnswer,
      "answer generation",
      "Generating answer...",
      (result) => setAnswer(result),
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
    <div className="bg-gradient-to-b from-white to-blue-50/30 dark:from-gray-950 dark:to-blue-950/30 relative" style={{ minHeight: 'max(100vh, 200vh)' }}>
      {/* Sidebar */}
      <Sidebar onLogout={handleLogout} />

      {/* Main Content */}
      <div className="relative">
        {/* Decorative background elements */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute left-1/4 top-1/4 h-48 w-48 md:h-64 md:w-64 rounded-full bg-blue-200/10 blur-3xl dark:bg-blue-900/10"></div>
          <div className="absolute right-1/4 bottom-1/3 h-64 w-64 md:h-96 md:w-96 rounded-full bg-purple-200/10 blur-3xl dark:bg-purple-900/10"></div>
        </div>

        {/* Main Content Area */}
        <div className="px-4 py-8 md:px-8 md:py-12 max-w-4xl mx-auto">
          {/* Header - hide after first generation */}
          {!hasGenerated && (
            <div className="text-center mb-8 md:mb-12 transition-all duration-500 ease-out">
              <h1 className="text-2xl md:text-3xl lg:text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent mb-2">
                {userData?.first_name ? `Good ${getGreeting()}, ${userData.first_name}` : "Welcome back"}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-sm md:text-base">
                Ready to create a tailored document for your next opportunity?
              </p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
                <div className="flex-1">
                  <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                  {isAuthError && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={redirectToLogin}
                      className="mt-2 text-red-600 border-red-300 hover:bg-red-50"
                    >
                      <LogIn className="h-4 w-4 mr-2" />
                      Log in again
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Main Input Area */}
          <div ref={inputAreaRef} className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 md:p-8 mb-8">
            <div className="space-y-6">
              {/* Job Description Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">
                  Job Description
                </label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here to instantly generate a tailored document..."
                  rows={6}
                  className="w-full px-4 py-3 text-sm border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 dark:bg-gray-800/50 dark:text-white dark:placeholder-gray-400 resize-none transition-all"
                />
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button
                  onClick={handleGenerateResume}
                  disabled={isGeneratingResume || !jobDescription.trim()}
                  className="h-14 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg disabled:opacity-50"
                >
                  {isGeneratingResume ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Generate Resume
                    </>
                  )}
                </Button>

                <Button
                  onClick={handleGenerateCoverLetter}
                  disabled={isGeneratingCoverLetter || !jobDescription.trim()}
                  className="h-14 bg-gradient-to-r from-violet-600 to-violet-700 hover:from-violet-700 hover:to-violet-800 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg disabled:opacity-50"
                >
                  {isGeneratingCoverLetter ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Mail className="mr-2 h-4 w-4" />
                      Generate Cover Letter
                    </>
                  )}
                </Button>

                <Button
                  onClick={() => setActiveTab('question')}
                  disabled={isGeneratingAnswer || !jobDescription.trim()}
                  className="h-14 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg disabled:opacity-50"
                >
                  <HelpCircle className="mr-2 h-4 w-4" />
                  Answer Question
                </Button>
              </div>

              {/* Resume Progress - Inline */}
              {showResumeProgress && (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <InlineResumeProgress 
                    isVisible={showResumeProgress}
                    forceComplete={forceCompleteProgress}
                    onComplete={handleResumeProgressComplete}
                  />
                </div>
              )}

              {/* Question Input (shown when Answer Question is selected) */}
              {activeTab === 'question' && (
                <div className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <label className="block text-sm font-semibold text-gray-800 dark:text-gray-200">
                    Application Question
                  </label>
                  <div className="relative">
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="Enter the application question you need to answer..."
                      rows={3}
                      className="w-full px-4 py-3 pr-24 text-sm border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 dark:bg-gray-800/50 dark:text-white dark:placeholder-gray-400 resize-none transition-all"
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault()
                          if (!isGeneratingAnswer && jobDescription.trim() && question.trim()) {
                            handleAnswerQuestion()
                          }
                        }
                      }}
                    />
                    <div className="absolute right-3 top-3 flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                      <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded border border-gray-300 dark:border-gray-600 font-mono text-xs flex items-center gap-1">
                        <span>Enter</span>
                        <span>↵</span>
                      </kbd>
                      <span>to generate</span>
                    </div>
                  </div>
                  <Button
                    onClick={handleAnswerQuestion}
                    disabled={isGeneratingAnswer || !jobDescription.trim() || !question.trim()}
                    className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg disabled:opacity-50"
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
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Your Tailored Resume
                    </h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleDownloadResume}
                        variant="outline"
                        size="sm"
                        className="text-blue-600 border-blue-200 hover:bg-blue-50"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download PDF
                      </Button>
                      <Button
                        onClick={handleDownloadTeX}
                        disabled={isDownloadingTeX}
                        variant="outline"
                        size="sm"
                        className="text-green-600 border-green-200 hover:bg-green-50"
                      >
                        {isDownloadingTeX ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <FileCode className="h-4 w-4 mr-2" />
                        )}
                        Download TeX
                      </Button>
                      <Button
                        onClick={handleOpenInOverleaf}
                        disabled={isPreparingOverleaf}
                        variant="outline"
                        size="sm"
                        className="text-orange-600 border-orange-200 hover:bg-orange-50"
                      >
                        {isPreparingOverleaf ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <ExternalLink className="h-4 w-4 mr-2" />
                        )}
                        Edit in Overleaf
                      </Button>
                    </div>
                  </div>
                  <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden">
                    <PdfViewer pdfUrl={generatedResumePdf} />
                  </div>
                </div>
              )}

              {/* Cover Letter Results */}
              {coverLetter && activeTab === 'cover-letter' && (
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Your Cover Letter
                    </h3>
                    <div className="flex gap-2">
                      <Button
                        onClick={handleCopyCoverLetter}
                        variant="outline"
                        size="sm"
                        className="text-blue-600 border-blue-200 hover:bg-blue-50"
                      >
                        <CopyIcon className="h-4 w-4 mr-2" />
                        {isCoverLetterCopied ? 'Copied!' : 'Copy'}
                      </Button>
                      <Button
                        onClick={handleDownloadCoverLetter}
                        disabled={isDownloadingCoverLetter}
                        variant="outline"
                        size="sm"
                        className="text-green-600 border-green-200 hover:bg-green-50"
                      >
                        {isDownloadingCoverLetter ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <Download className="h-4 w-4 mr-2" />
                        )}
                        Download PDF
                      </Button>
                    </div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-mono">
                      {coverLetter}
                    </pre>
                  </div>
                </div>
              )}

              {/* Answer Results */}
              {answer && activeTab === 'question' && (
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      Your Answer
                    </h3>
                    <Button
                      onClick={handleCopyAnswer}
                      variant="outline"
                      size="sm"
                      className="text-blue-600 border-blue-200 hover:bg-blue-50"
                    >
                      <CopyIcon className="h-4 w-4 mr-2" />
                      {isAnswerCopied ? 'Copied!' : 'Copy Answer'}
                    </Button>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 dark:text-gray-300 font-mono">
                      {answer}
                    </pre>
                  </div>
                </div>
              )}

              {/* Enhanced Glassmorphism Make it Better Section */}
              {((activeTab === 'resume' && generatedResumePdf) || 
                (activeTab === 'cover-letter' && coverLetter) || 
                (activeTab === 'question' && answer)) && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 w-full max-w-4xl px-4 md:px-8 z-40 animate-in slide-in-from-bottom-4 fade-in duration-500">
                  <div className="bg-white/15 dark:bg-gray-900/15 backdrop-blur-2xl rounded-2xl shadow-2xl border border-white/30 dark:border-gray-700/30 p-4">
                    {/* Single line: title first, then quick actions */}
                    <div className="flex items-center gap-3 mb-3 flex-wrap">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-5 w-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                          Make it better
                        </h3>
                      </div>
                      
                      <button
                        onClick={() => handleQuickAction("Make it shorter and more concise")}
                        disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        className="px-2.5 py-1 text-xs font-medium rounded-full bg-blue-500/10 hover:bg-blue-500/20 text-blue-700 dark:text-blue-300 border border-blue-200/50 dark:border-blue-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        ✂️ Make shorter
                      </button>
                      <button
                        onClick={() => handleQuickAction("Make the tone more formal and professional")}
                        disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        className="px-2.5 py-1 text-xs font-medium rounded-full bg-purple-500/10 hover:bg-purple-500/20 text-purple-700 dark:text-purple-300 border border-purple-200/50 dark:border-purple-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        👔 More formal
                      </button>
                      <button
                        onClick={() => handleQuickAction("Make the tone more casual and approachable")}
                        disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        className="px-2.5 py-1 text-xs font-medium rounded-full bg-orange-500/10 hover:bg-orange-500/20 text-orange-700 dark:text-orange-300 border border-orange-200/50 dark:border-orange-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        😊 More casual
                      </button>
                      <button
                        onClick={() => handleQuickAction("Add more technical skills and keywords relevant to the job")}
                        disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        className="px-2.5 py-1 text-xs font-medium rounded-full bg-violet-500/10 hover:bg-violet-500/20 text-violet-700 dark:text-violet-300 border border-violet-200/50 dark:border-violet-700/50 transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        🔑 Add keywords
                      </button>
                    </div>

                    {/* Compact Custom Input */}
                    <div className="flex gap-3">
                      <div className="flex-1 relative">
                        <input
                          type="text"
                          value={followUpInstruction}
                          onChange={(e) => setFollowUpInstruction(e.target.value)}
                          placeholder="Or describe what you want to improve..."
                          className="w-full h-12 px-4 pr-16 text-sm bg-white/20 dark:bg-gray-800/20 backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 dark:text-white dark:placeholder-gray-400 transition-all"
                          onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                              e.preventDefault()
                              handleFollowUpSubmit()
                            }
                          }}
                          disabled={isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        />
                        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                          <kbd className="px-2 py-1 bg-gray-100/70 dark:bg-gray-700/70 rounded border border-gray-300/50 dark:border-gray-600/50 font-mono text-xs flex items-center gap-1 backdrop-blur-sm">
                            <span>Enter</span>
                            <span>↵</span>
                          </kbd>
                          <span>to update</span>
                        </div>
                      </div>
                      <Button
                        type="button"
                        onClick={handleFollowUpSubmit}
                        disabled={!followUpInstruction.trim() || isEditingResume || isEditingCoverLetter || isEditingAnswer}
                        className="h-12 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-all duration-200 hover:shadow-lg disabled:opacity-50"
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