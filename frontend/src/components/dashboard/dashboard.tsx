"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { getUserData, removeAccessToken, removeUserData } from "@/lib/utils"
import { applications, preferences } from "@/lib/api"
import PdfViewer from "@/components/pdf-viewer"
import PreferencesPrompt from "@/components/ui/preferences-prompt"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, Loader2, FileCode, ExternalLink, AlertCircle, MessageSquare } from "lucide-react"
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
  const [coverLetterEditInstruction, setCoverLetterEditInstruction] = useState('')
  const [isEditingCoverLetter, setIsEditingCoverLetter] = useState(false)
  const [downloadCoverLetterUrl, setDownloadCoverLetterUrl] = useState<string | null>(null)
  const [answerEditInstruction, setAnswerEditInstruction] = useState('')
  const [isEditingAnswer, setIsEditingAnswer] = useState(false)
  
  // Preferences prompt state
  const [showPreferencesPrompt, setShowPreferencesPrompt] = useState(false)
  const [currentEditInstruction, setCurrentEditInstruction] = useState("")

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
      async () => {
        // If we have a downloadCoverLetterUrl from a recent edit, use that
        if (downloadCoverLetterUrl) {
          const response = await fetch(downloadCoverLetterUrl);
          return await response.blob();
        }
        // Otherwise fetch from the API
        return applications.getCoverLetterPDF();
      },
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
    
    // Show preferences prompt immediately
    setCurrentEditInstruction(editInstruction)
    setShowPreferencesPrompt(true)
    
    asyncOperation(
      () => applications.editResumeWithInstructions(
        editInstruction,
        jobDescription
      ),
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
      () => {
        if (!editInstruction.trim()) return "Please enter edit instructions"
        if (!jobDescription.trim()) return "Please ensure there is a job description"
        return null
      }
    )
  }

  const handleEditCoverLetter = () => {
    if (!coverLetter) {
      setError("Please generate a cover letter first before editing.")
      return
    }
    
    // Show preferences prompt immediately
    setCurrentEditInstruction(coverLetterEditInstruction)
    setShowPreferencesPrompt(true)
    
    asyncOperation(
      () => applications.editCoverLetterWithInstructions(
        coverLetterEditInstruction,
        jobDescription
      ),
      setIsEditingCoverLetter,
      "cover letter editing",
      "Updating cover letter...",
      async (result) => {
        // Create a URL for the PDF
        const pdfUrl = URL.createObjectURL(result)
        setDownloadCoverLetterUrl(pdfUrl)
        
        // Fetch the updated cover letter text
        try {
          const updatedText = await applications.getCoverLetterText()
          if (updatedText) {
            setCoverLetter(updatedText)
          }
        } catch (err) {
          console.error("Error fetching updated cover letter text:", err)
          // Continue even if text fetch fails
        }
        
        setCoverLetterEditInstruction("") // Clear the edit instruction field
      },
      "Failed to update cover letter with instructions. Please check your input.",
      () => {
        if (!coverLetterEditInstruction.trim()) return "Please enter edit instructions"
        if (!jobDescription.trim()) return "Please ensure there is a job description"
        return null
      }
    )
  }

  const handleEditAnswer = () => {
    if (!answer) {
      setError("Please generate an answer first before editing.")
      return
    }
    
    // Show preferences prompt immediately
    setCurrentEditInstruction(answerEditInstruction)
    setShowPreferencesPrompt(true)
    
    asyncOperation(
      () => applications.editAnswerWithInstructions(
        answerEditInstruction,
        answer,
        question,
        jobDescription
      ),
      setIsEditingAnswer,
      "answer editing",
      "Updating answer...",
      (result) => {
        // Update the answer with the result from the API (now a plain string)
        if (result) {
          setAnswer(result)
        }
        setAnswerEditInstruction("") // Clear the edit instruction field
      },
      "Failed to update answer with instructions. Please check your input.",
      () => !answerEditInstruction.trim() ? "Please enter edit instructions" : null
    )
  }

  const handleSavePreference = async (preference: string) => {
    try {
      await preferences.addUserPreference(preference)
      console.log('Preference saved successfully:', preference)
    } catch (error) {
      console.error('Failed to save preference:', error)
      setError('Failed to save preference. Please try again.')
      throw error; // Re-throw to let the prompt handle the error
    }
  }

  const handleDismissPreferencesPrompt = () => {
    setShowPreferencesPrompt(false)
    setCurrentEditInstruction("")
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
                        
                        {/* Preferences Prompt for Resume */}
                        {showPreferencesPrompt && (
                          <PreferencesPrompt
                            isVisible={showPreferencesPrompt}
                            editInstruction={currentEditInstruction}
                            onSavePreference={handleSavePreference}
                            onDismiss={handleDismissPreferencesPrompt}
                          />
                        )}
                        
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

        <TabsContent value="cover" className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold">Your Cover Letter</h2>
              <div className="flex space-x-3">
                <Button
                  onClick={handleGenerateCoverLetter}
                  disabled={isGeneratingCoverLetter || !jobDescription.trim()}
                  className="bg-emerald-600 hover:bg-emerald-700"
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
                  <Button
                    variant="outline"
                    onClick={handleDownloadCoverLetter}
                    disabled={isDownloadingCoverLetter}
                  >
                    {isDownloadingCoverLetter ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Download className="h-4 w-4 mr-1" />
                        Download PDF
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>

            {!jobDescription.trim() && (
              <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded relative">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span className="block sm:inline">Please enter a job description in the "Generate Resume" tab first.</span>
                </div>
              </div>
            )}

            {/* Cover Letter Content Area */}
            <div className="flex-grow flex flex-col">
              {coverLetter ? (
                <>
                  {/* Cover Letter Text Area */}
                  <div className="flex-grow border border-gray-300 rounded-t-md bg-gray-50 p-4">
                    <textarea
                      value={coverLetter}
                      onChange={(e) => setCoverLetter(e.target.value)}
                      className="w-full h-full p-3 border border-gray-300 rounded-md resize-none"
                      style={{ minHeight: "300px" }}
                    />
                  </div>
                  
                  {/* AI Cover Letter Editor */}
                  <div className="border border-t-0 border-gray-300 rounded-b-md bg-gray-50 p-4">
                    <div className="flex items-start mb-3">
                      <div className="bg-emerald-100 p-2 rounded-full mr-3">
                        <MessageSquare className="h-5 w-5 text-emerald-700" />
                      </div>
                      <div className="bg-emerald-50 text-emerald-800 p-3 rounded-lg rounded-tl-none max-w-[85%]">
                        <p className="text-sm">
                          I can help you refine your cover letter with AI. Simply tell me what you'd like to change:
                        </p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <span 
                            className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                            onClick={() => setCoverLetterEditInstruction("Make the tone more professional")}
                          >
                            More professional tone
                          </span>
                          <span 
                            className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                            onClick={() => setCoverLetterEditInstruction("Highlight my leadership experience")}
                          >
                            Highlight leadership
                          </span>
                          <span 
                            className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                            onClick={() => setCoverLetterEditInstruction("Make it more concise")}
                          >
                            More concise
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Preferences Prompt for Cover Letter */}
                    {showPreferencesPrompt && (
                      <PreferencesPrompt
                        isVisible={showPreferencesPrompt}
                        editInstruction={currentEditInstruction}
                        onSavePreference={handleSavePreference}
                        onDismiss={handleDismissPreferencesPrompt}
                      />
                    )}
                    
                    <div className="flex items-end mt-3">
                      <input
                        type="text"
                        className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        placeholder="Describe what you want to change..."
                        value={coverLetterEditInstruction}
                        onChange={(e) => setCoverLetterEditInstruction(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && coverLetterEditInstruction.trim() && !isEditingCoverLetter) {
                            handleEditCoverLetter();
                          }
                        }}
                        style={{ height: '44px' }}
                      />
                      <Button 
                        onClick={handleEditCoverLetter}
                        disabled={isEditingCoverLetter || !coverLetterEditInstruction.trim()}
                        className="bg-emerald-600 hover:bg-emerald-700 rounded-l-none h-[44px] flex items-center justify-center"
                      >
                        {isEditingCoverLetter ? (
                          <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                            <path d="m5 11 4 4L19 7" />
                          </svg>
                        )}
                      </Button>
                    </div>
                    {isEditingCoverLetter && (
                      <p className="text-xs text-gray-500 mt-2 flex items-center">
                        <Loader2 className="h-3 w-3 animate-spin mr-1" />
                        Updating your cover letter...
                      </p>
                    )}
                  </div>
                </>
              ) : (
                <div className="flex-grow border border-gray-300 rounded-md flex flex-col items-center justify-center bg-gray-50 text-center p-8">
                  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-4">
                    <path d="M21 14h-8a2 2 0 0 0-2 2v.5A2.5 2.5 0 0 0 13.5 19h1a2.5 2.5 0 0 0 2.5-2.5V16a2 2 0 0 0-2-2h-8M3 8h18M3 12h18M3 16h6M3 20h6" />
                  </svg>
                  <h3 className="text-lg font-medium text-gray-700 mb-2">No Cover Letter Generated Yet</h3>
                  <p className="text-gray-500 max-w-md">
                    Click "Generate Cover Letter" to create a tailored letter based on your job description from the Resume tab.
                  </p>
                </div>
              )}
            </div>
          </div>
        </TabsContent>

            <TabsContent value="questions" className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Application Questions</h2>
                <Button
                  onClick={handleAnswerQuestion}
                  disabled={isGeneratingAnswer || !jobDescription.trim() || !question.trim()}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  {isGeneratingAnswer ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Answer...
                    </>
                  ) : (
                    "Generate Answer"
                  )}
                </Button>
              </div>

              {!jobDescription.trim() && (
                <div className="mb-4 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded relative">
                  <div className="flex items-center">
                    <AlertCircle className="h-5 w-5 mr-2" />
                    <span className="block sm:inline">Please enter a job description in the "Generate Resume" tab first.</span>
                  </div>
                </div>
              )}

              <div className="mb-4">
                <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1">
                  Question
                </label>
                <textarea
                  id="question"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Enter the application question..."
                  className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  rows={3}
                />
              </div>
              
              {/* Answer Content Area */}
              <div className="flex-grow flex flex-col">
                {answer ? (
                  <>
                    <div className="border border-gray-300 rounded-t-md bg-gray-50 p-4">
                      <textarea
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        className="w-full h-full p-3 border border-gray-300 rounded-md resize-none"
                        style={{ minHeight: "200px" }}
                        placeholder="Your generated answer will appear here..."
                      />
                    </div>
                    
                    {/* AI Answer Editor */}
                    <div className="border border-t-0 border-gray-300 rounded-b-md bg-gray-50 p-4">
                      <div className="flex items-start mb-3">
                        <div className="bg-emerald-100 p-2 rounded-full mr-3">
                          <MessageSquare className="h-5 w-5 text-emerald-700" />
                        </div>
                        <div className="bg-emerald-50 text-emerald-800 p-3 rounded-lg rounded-tl-none max-w-[85%]">
                          <p className="text-sm">
                            I can help you refine your answer with AI. Simply tell me what you'd like to change:
                          </p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            <span 
                              className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                              onClick={() => setAnswerEditInstruction("Make the answer more detailed")}
                            >
                              More detailed
                            </span>
                            <span 
                              className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                              onClick={() => setAnswerEditInstruction("Highlight specific achievements")}
                            >
                              Highlight achievements
                            </span>
                            <span 
                              className="inline-block px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs cursor-pointer hover:bg-emerald-200"
                              onClick={() => setAnswerEditInstruction("Make it more concise")}
                            >
                              More concise
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Preferences Prompt for Answer */}
                      {showPreferencesPrompt && (
                        <PreferencesPrompt
                          isVisible={showPreferencesPrompt}
                          editInstruction={currentEditInstruction}
                          onSavePreference={handleSavePreference}
                          onDismiss={handleDismissPreferencesPrompt}
                        />
                      )}
                      
                      <div className="flex items-end mt-3">
                        <input
                          type="text"
                          className="flex-grow p-3 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                          placeholder="Describe what you want to change..."
                          value={answerEditInstruction}
                          onChange={(e) => setAnswerEditInstruction(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' && answerEditInstruction.trim() && !isEditingAnswer) {
                              handleEditAnswer();
                            }
                          }}
                          style={{ height: '44px' }}
                        />
                        <Button 
                          onClick={handleEditAnswer}
                          disabled={isEditingAnswer || !answerEditInstruction.trim()}
                          className="bg-emerald-600 hover:bg-emerald-700 rounded-l-none h-[44px] flex items-center justify-center"
                        >
                          {isEditingAnswer ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
                              <path d="m5 11 4 4L19 7" />
                            </svg>
                          )}
                        </Button>
                      </div>
                      {isEditingAnswer && (
                        <p className="text-xs text-gray-500 mt-2 flex items-center">
                          <Loader2 className="h-3 w-3 animate-spin mr-1" />
                          Updating your answer...
                        </p>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="flex-grow border border-gray-300 rounded-md flex flex-col items-center justify-center bg-gray-50 text-center p-8">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-4">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                      <path d="M12 17h.01" />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-700 mb-2">No Answer Generated Yet</h3>
                    <p className="text-gray-500 max-w-md">
                      Enter an application question above and click "Generate Answer" to create a tailored response based on your job description.
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
    </div>
  )
} 