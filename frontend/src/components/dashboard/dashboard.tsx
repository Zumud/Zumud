"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { getUserData, removeAccessToken, removeUserData } from "@/lib/utils"
import { applications } from "@/lib/api"
import PdfViewer from "@/components/pdf-viewer"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, Loader2, FileCode, ExternalLink, AlertCircle } from "lucide-react"
import Link from "next/link"

export default function Dashboard() {
  const [userData, setUserData] = useState<any>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")
  const [coverLetter, setCoverLetter] = useState("")
  const [isGeneratingResume, setIsGeneratingResume] = useState(false)
  const [isGeneratingCoverLetter, setIsGeneratingCoverLetter] = useState(false)
  const [isGeneratingAnswer, setIsGeneratingAnswer] = useState(false)
  const [generatedResumePdf, setGeneratedResumePdf] = useState<string | null>(null)
  const [isDownloadingTeX, setIsDownloadingTeX] = useState(false)
  const [isDownloadingCoverLetter, setIsDownloadingCoverLetter] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isPreparingOverleaf, setIsPreparingOverleaf] = useState(false)

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

  // Reusable function to handle errors, especially timeouts
  const handleError = (err: any, defaultMessage: string) => {
    console.error(defaultMessage, err)
    
    if (err.name === 'AbortError' || (err.message && err.message.includes("took too long to complete"))) {
      setError("Timeout: The request took too long to complete. Try again with a shorter job description.")
    } else {
      setError(err.message || defaultMessage)
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
        return
      }
    }

    setLoading(true)
    setError(null)
    
    // Set a processing message after 5 seconds
    const processingMessageTimeout = setTimeout(() => {
      setError(processingMessage)
    }, 5000)

    try {
      const result = await operation()
      setError(null)
      onSuccess(result)
    } catch (err: any) {
      handleError(err, defaultErrorMessage)
    } finally {
      clearTimeout(processingMessageTimeout)
      setLoading(false)
    }
  }

  const handleGenerateResume = () => {
    asyncOperation(
      // Operation to perform
      () => applications.generateResume(jobDescription),
      // Set loading state
      setIsGeneratingResume,
      // Operation name 
      "resume generation",
      // Processing message
      "Processing your request. Resume generation may take up to a minute for complex job descriptions...",
      // Success handler
      (result) => {
        const pdfUrl = URL.createObjectURL(result)
        setGeneratedResumePdf(pdfUrl)
      },
      // Default error message
      "Failed to generate resume",
      // Validation
      () => !jobDescription.trim() ? "Please enter a job description" : null
    )
  }

  const handleGenerateCoverLetter = () => {
    asyncOperation(
      () => applications.generateCoverLetter(jobDescription),
      setIsGeneratingCoverLetter,
      "cover letter generation",
      "Processing your request. Cover letter generation may take up to a minute for complex job descriptions...",
      (result) => setCoverLetter(result),
      "Failed to generate cover letter",
      () => !jobDescription.trim() ? "Please enter a job description" : null
    )
  }

  const handleAnswerQuestion = () => {
    asyncOperation(
      () => applications.answerQuestion(jobDescription, question),
      setIsGeneratingAnswer,
      "answer generation",
      "Processing your request. This may take up to a minute...",
      (result) => setAnswer(result),
      "Failed to generate answer",
      () => {
        if (!jobDescription.trim()) return "Please enter a job description"
        if (!question.trim()) return "Please enter a question"
        return null
      }
    )
  }

  const handleDownloadResume = () => {
    if (generatedResumePdf) {
      const link = document.createElement("a")
      link.href = generatedResumePdf
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      link.download = `tailored_resume_${timestamp}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleDownloadTeX = () => {
    asyncOperation(
      () => applications.getResumeTeX(),
      setIsDownloadingTeX,
      "tex file download",
      "Processing your request. This may take up to a minute...",
      (result) => {
        if (!result) {
          throw new Error("Received empty response from server")
        }
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        downloadBlob(result, `tailored_resume_${timestamp}.tex`)
      },
      "Failed to download .tex file. Make sure you have generated a resume first."
    )
  }

  const handleOpenInOverleaf = () => {
    asyncOperation(
      () => applications.getResumeTeXContent(),
      setIsPreparingOverleaf,
      "Overleaf preparation",
      "Processing your request. This may take up to a minute...",
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
      "Failed to open in Overleaf. Make sure you have generated a resume first."
    )
  }

  const handleDownloadCoverLetter = () => {
    asyncOperation(
      () => applications.getCoverLetterPDF(),
      setIsDownloadingCoverLetter,
      "cover letter PDF download",
      "Processing your request. This may take up to a minute...",
      (result) => {
        if (!result) {
          throw new Error("Received empty response from server")
        }
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
        downloadBlob(result, `cover_letter_${timestamp}.pdf`)
      },
      "Failed to download cover letter PDF. Make sure you have generated a cover letter first.",
      () => !coverLetter ? "Please generate a cover letter first" : null
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Welcome, {userData?.username || 'User'}!</h1>
        <div className="flex space-x-4">
          <Link href="/profile">
            <Button variant="outline">
              Profile Settings
            </Button>
          </Link>
          <Button
            variant="outline"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>
      </header>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span className="block sm:inline">{error}</span>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Job Description Section */}
        <div className="md:col-span-1 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Job Description</h2>
          <textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-64 p-3 border border-gray-300 rounded-md"
          />
        </div>

        {/* Main Content Area */}
        <div className="md:col-span-2">
          <Tabs defaultValue="resume">
            <TabsList className="mb-4">
              <TabsTrigger value="resume">Generate Resume</TabsTrigger>
              <TabsTrigger value="cover-letter">Cover Letter</TabsTrigger>
              <TabsTrigger value="questions">Answer Questions</TabsTrigger>
            </TabsList>

            <TabsContent value="resume" className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Create Tailored Resume</h2>
              <Button
                onClick={handleGenerateResume}
                disabled={isGeneratingResume || !jobDescription.trim()}
                className="mb-4 bg-emerald-600 hover:bg-emerald-700"
              >
                {isGeneratingResume ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  "Generate Resume"
                )}
              </Button>

              {generatedResumePdf && (
                <div className="mt-4">
                  <PdfViewer pdfUrl={generatedResumePdf} />
                  <div className="flex flex-wrap gap-2 mt-4">
                    <Button
                      onClick={handleDownloadResume}
                      className="bg-emerald-600 hover:bg-emerald-700"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Download Resume
                    </Button>
                    <Button
                      onClick={handleDownloadTeX}
                      className="bg-blue-600 hover:bg-blue-700"
                      disabled={isDownloadingTeX}
                    >
                      {isDownloadingTeX ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Downloading...
                        </>
                      ) : (
                        <>
                          <FileCode className="mr-2 h-4 w-4" />
                          Download .tex File
                        </>
                      )}
                    </Button>
                    <Button
                      onClick={handleOpenInOverleaf}
                      className="bg-orange-600 hover:bg-orange-700"
                      disabled={isPreparingOverleaf}
                    >
                      {isPreparingOverleaf ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Preparing...
                        </>
                      ) : (
                        <>
                          <ExternalLink className="mr-2 h-4 w-4" />
                          Edit in Overleaf
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="cover-letter" className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Generate Cover Letter</h2>
              <Button
                onClick={handleGenerateCoverLetter}
                disabled={isGeneratingCoverLetter || !jobDescription.trim()}
                className="mb-4 bg-emerald-600 hover:bg-emerald-700"
              >
                {isGeneratingCoverLetter ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  "Generate Cover Letter"
                )}
              </Button>

              {coverLetter && (
                <>
                  <div className="mt-4 border border-gray-200 rounded-md p-4 bg-gray-50">
                    <textarea
                      value={coverLetter}
                      onChange={(e) => setCoverLetter(e.target.value)}
                      className="w-full h-80 p-3 border border-gray-300 rounded-md"
                      readOnly={false}
                    />
                  </div>
                  <div className="mt-4 flex justify-end">
                    <Button
                      onClick={handleDownloadCoverLetter}
                      disabled={isDownloadingCoverLetter}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isDownloadingCoverLetter ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Downloading...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Download PDF
                        </>
                      )}
                    </Button>
                  </div>
                </>
              )}
            </TabsContent>

            <TabsContent value="questions" className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Answer Application Questions</h2>
              <div className="mb-4">
                <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1">
                  Question
                </label>
                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Enter the application question..."
                  className="w-full h-24 p-3 border border-gray-300 rounded-md"
                />
              </div>
              
              <Button
                onClick={handleAnswerQuestion}
                disabled={isGeneratingAnswer || !jobDescription.trim() || !question.trim()}
                className="mb-4 bg-emerald-600 hover:bg-emerald-700"
              >
                {isGeneratingAnswer ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  "Generate Answer"
                )}
              </Button>

              {answer && (
                <div className="mt-4 border border-gray-200 rounded-md p-4 bg-gray-50">
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    className="w-full h-48 p-3 border border-gray-300 rounded-md"
                    readOnly={false}
                  />
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
} 