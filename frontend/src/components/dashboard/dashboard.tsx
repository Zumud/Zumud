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
  const [editInstruction, setEditInstruction] = useState("")
  const [isEditingResume, setIsEditingResume] = useState(false)
  const [updatedResumeJson, setUpdatedResumeJson] = useState<string | null>(null)
  const [lastGeneratedResumeJson, setLastGeneratedResumeJson] = useState<string | null>(null)

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
    
    try {
      const result = await operation()
      setError(null)
      onSuccess(result)
    } catch (err: any) {
      handleError(err, defaultErrorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateResume = () => {
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
      "Generating cover letter...",
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
      "Preparing TeX file...",
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
      "Preparing for Overleaf...",
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
      "Preparing PDF...",
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

  const handleEditResume = () => {
    if (!generatedResumePdf) {
      setError("Please generate a resume first before editing.")
      return
    }
    
    asyncOperation(
      () => applications.editResumeWithInstructions(editInstruction),
      setIsEditingResume,
      "resume editing",
      "Updating resume...",
      (result) => {
        // The result is now a PDF blob
        const pdfUrl = URL.createObjectURL(result)
        setGeneratedResumePdf(pdfUrl)
        setEditInstruction("") // Clear the edit instruction field
      },
      "Failed to update resume with instructions. Please check your input.",
      () => !editInstruction.trim() ? "Please enter edit instructions" : null
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

      <Tabs defaultValue="generate" className="w-full">
        <TabsList className="grid grid-cols-3 mb-8">
          <TabsTrigger value="generate">Generate Resume</TabsTrigger>
          <TabsTrigger value="cover">Cover Letter</TabsTrigger>
          <TabsTrigger value="questions">Application Questions</TabsTrigger>
        </TabsList>

        <TabsContent value="generate" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-6 gap-6">
            {/* Left panel - Job Description (reduced width) */}
            <div className="lg:col-span-2">
              <div className="bg-white p-6 rounded-lg shadow h-full flex flex-col">
          <h2 className="text-xl font-semibold mb-4">Job Description</h2>
          <textarea
                  className="w-full flex-grow p-4 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 mb-4"
                  placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
                />
              <Button
                  className="w-full bg-emerald-600 hover:bg-emerald-700" 
                onClick={handleGenerateResume}
                  disabled={isGeneratingResume}
              >
                {isGeneratingResume ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Resume...
                  </>
                ) : (
                  "Generate Resume"
                )}
              </Button>
              </div>
            </div>

            {/* Right panel - Resume Preview & Chat-like Edit Interface (increased width) */}
            <div className="lg:col-span-4">
              <div className="bg-white p-6 rounded-lg shadow h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold">Your Resume</h2>
              {generatedResumePdf && (
                    <div className="flex space-x-2">
                    <Button
                        size="sm"
                        variant="outline"
                      onClick={handleDownloadResume}
                    >
                        <Download className="h-4 w-4 mr-1" />
                        PDF
                    </Button>
                    <Button
                        size="sm"
                        variant="outline"
                      onClick={handleDownloadTeX}
                      disabled={isDownloadingTeX}
                    >
                      {isDownloadingTeX ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                            <FileCode className="h-4 w-4 mr-1" />
                            TEX
                        </>
                      )}
                    </Button>
                    <Button
                        size="sm"
                        variant="outline"
                      onClick={handleOpenInOverleaf}
                      disabled={isPreparingOverleaf}
                    >
                      {isPreparingOverleaf ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                            <ExternalLink className="h-4 w-4 mr-1" />
                          Edit in Overleaf
                        </>
                      )}
                    </Button>
                  </div>
                  )}
                </div>

                {/* Resume Workspace with PDF and Chat-style editing */}
                <div className="flex-grow flex flex-col">
                  {generatedResumePdf ? (
                    <>
                      {/* PDF Preview Area */}
                      <div className="h-96 border border-gray-300 rounded-t-md overflow-hidden">
                        <PdfViewer pdfUrl={generatedResumePdf} />
                      </div>
                      
                      {/* AI Resume Editor */}
                      <div className="border border-t-0 border-gray-300 rounded-b-md bg-gray-50 p-4">
                        <div className="flex items-start mb-3">
                          <div className="bg-emerald-100 p-2 rounded-full mr-3">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-700">
                              <path d="M12 8V16M8 12H16" />
                            </svg>
                          </div>
                          <div className="bg-emerald-50 text-emerald-800 p-3 rounded-lg rounded-tl-none max-w-[85%]">
                            <p className="text-sm">
                              I can help you refine your resume with AI. Simply tell me what you'd like to change, such as:
                            </p>
                            <div className="mt-2 flex flex-wrap gap-2">
                              <span 
                                className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                                onClick={() => setEditInstruction("Add AWS to my skills section")}
                              >
                                Add AWS to skills
                              </span>
                              <span 
                                className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                                onClick={() => setEditInstruction("Update my job title to Senior Developer")}
                              >
                                Update job title
                              </span>
                              <span 
                                className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                                onClick={() => setEditInstruction("Add a new project with React and TypeScript")}
                              >
                                Add a project
                              </span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-end mt-3">
                          <input
                            type="text"
                            className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            placeholder="Describe what you want to change..."
                            value={editInstruction}
                            onChange={(e) => setEditInstruction(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' && editInstruction.trim() && !isEditingResume) {
                                handleEditResume();
                              }
                            }}
                            style={{ height: '44px' }}
                          />
                          <Button 
                            onClick={handleEditResume}
                            disabled={isEditingResume || !editInstruction.trim()}
                            className="bg-emerald-600 hover:bg-emerald-700 rounded-l-none h-[44px] flex items-center justify-center"
                          >
                            {isEditingResume ? (
                              <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                                <path d="m5 11 4 4L19 7" />
                              </svg>
                            )}
                          </Button>
                        </div>
                        {isEditingResume && (
                          <p className="text-xs text-gray-500 mt-2 flex items-center">
                            <Loader2 className="h-3 w-3 animate-spin mr-1" />
                            Updating your resume...
                          </p>
                        )}
                      </div>
                    </>
                  ) : (
                    <div className="flex-grow border border-gray-300 rounded-md flex flex-col items-center justify-center bg-gray-50 text-center p-8">
                      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-4">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-700 mb-2">No Resume Generated Yet</h3>
                      <p className="text-gray-500 max-w-md">
                        Paste a job description in the left panel and click "Generate Resume" to create a tailored resume for your application.
                      </p>
                </div>
              )}
                </div>
              </div>
            </div>
          </div>
            </TabsContent>

        <TabsContent value="cover" className="bg-white p-6 rounded-lg shadow">
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
  )
} 