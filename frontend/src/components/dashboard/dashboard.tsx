"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { getUserData, removeAccessToken, removeUserData } from "@/lib/utils"
import { resume, applications } from "@/lib/api"
import PdfViewer from "@/components/pdf-viewer"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Download, Loader2, FileCode, ExternalLink } from "lucide-react"
import ProfileSettings from "./profile-settings"

export default function Dashboard() {
  const [userData, setUserData] = useState<any>(null)
  const [resumeData, setResumeData] = useState<string>("")
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
  const [showProfileSettings, setShowProfileSettings] = useState(false)
  const [isPreparingOverleaf, setIsPreparingOverleaf] = useState(false)

  // Load user data on mount
  useEffect(() => {
    const storedUserData = getUserData()
    if (storedUserData) {
      setUserData(storedUserData)
      fetchResumeData()
    }
  }, [])

  const fetchResumeData = async () => {
    try {
      const data = await resume.getResume()
      if (data && data.resume_content) {
        setResumeData(data.resume_content)
      }
    } catch (err: any) {
      console.error('Failed to load resume:', err)
    }
  }

  const handleUpdateResume = async () => {
    try {
      await resume.updateResume(resumeData)
      alert('Resume updated successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to update resume')
    }
  }

  const handleLogout = () => {
    removeAccessToken()
    removeUserData()
    window.location.reload()
  }

  const handleGenerateResume = async () => {
    if (!jobDescription.trim()) {
      setError("Please enter a job description")
      return
    }

    setIsGeneratingResume(true)
    setError(null)

    try {
      // The API now directly returns a PDF blob
      const result = await applications.generateResume(jobDescription)
      
      // Create a URL for the PDF blob
      const pdfUrl = URL.createObjectURL(result)
      setGeneratedResumePdf(pdfUrl)
    } catch (err: any) {
      setError(err.message || 'Failed to generate resume')
    } finally {
      setIsGeneratingResume(false)
    }
  }

  const handleGenerateCoverLetter = async () => {
    if (!jobDescription.trim()) {
      setError("Please enter a job description")
      return
    }

    setIsGeneratingCoverLetter(true)
    setError(null)

    try {
      const result = await applications.generateCoverLetter(jobDescription)
      setCoverLetter(result)
    } catch (err: any) {
      setError(err.message || 'Failed to generate cover letter')
    } finally {
      setIsGeneratingCoverLetter(false)
    }
  }

  const handleAnswerQuestion = async () => {
    if (!jobDescription.trim() || !question.trim()) {
      setError("Please enter both a job description and a question")
      return
    }

    setIsGeneratingAnswer(true)
    setError(null)

    try {
      const result = await applications.answerQuestion(jobDescription, question)
      setAnswer(result)
    } catch (err: any) {
      setError(err.message || 'Failed to generate answer')
    } finally {
      setIsGeneratingAnswer(false)
    }
  }

  const handleDownloadResume = () => {
    if (generatedResumePdf) {
      const link = document.createElement("a")
      link.href = generatedResumePdf
      // Use a more descriptive filename that includes timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      link.download = `tailored_resume_${timestamp}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleDownloadTeX = async () => {
    setIsDownloadingTeX(true)
    setError(null)

    try {
      console.log("Requesting .tex file from API")
      const result = await applications.getResumeTeX()
      console.log("Received response:", result)
      
      // Check if we got a valid result
      if (!result) {
        throw new Error("Received empty response from server")
      }
      
      // Create a URL for the tex file blob
      const texUrl = URL.createObjectURL(result)
      console.log("Created blob URL:", texUrl)
      
      const link = document.createElement("a")
      link.href = texUrl
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      link.download = `tailored_resume_${timestamp}.tex`
      document.body.appendChild(link)
      console.log("Starting download")
      link.click()
      document.body.removeChild(link)
      
      // Release the blob URL
      setTimeout(() => {
        URL.revokeObjectURL(texUrl)
        console.log("Revoked blob URL")
      }, 1000)
    } catch (err: any) {
      console.error("Download .tex file error:", err)
      setError(err.message || 'Failed to download .tex file. Make sure you have generated a resume first.')
    } finally {
      setIsDownloadingTeX(false)
    }
  }

  const handleOpenInOverleaf = async () => {
    setIsPreparingOverleaf(true)
    setError(null)

    try {
      console.log("Requesting .tex content for Overleaf")
      const texContent = await applications.getResumeTeXContent()
      console.log("Received .tex content")

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
      console.log("Submitting to Overleaf")
      form.submit()
      document.body.removeChild(form)

    } catch (err: any) {
      console.error("Open in Overleaf error:", err)
      setError(err.message || 'Failed to open in Overleaf. Make sure you have generated a resume first.')
    } finally {
      setIsPreparingOverleaf(false)
    }
  }

  const handleDownloadCoverLetter = async () => {
    if (!coverLetter) {
      setError("Please generate a cover letter first")
      return
    }
    
    setIsDownloadingCoverLetter(true)
    setError(null)

    try {
      const result = await applications.getCoverLetterPDF()
      
      if (!result) {
        throw new Error("Received empty response from server")
      }
      
      const pdfUrl = URL.createObjectURL(result)
      
      const link = document.createElement("a")
      link.href = pdfUrl
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
      link.download = `cover_letter_${timestamp}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      setTimeout(() => {
        URL.revokeObjectURL(pdfUrl)
      }, 1000)
    } catch (err: any) {
      console.error("Download cover letter error:", err)
      setError(err.message || 'Failed to download cover letter PDF. Make sure you have generated a cover letter first.')
    } finally {
      setIsDownloadingCoverLetter(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Welcome, {userData?.username || 'User'}!</h1>
        <div className="flex space-x-4">
          <Button
            variant="outline"
            onClick={() => setShowProfileSettings(true)}
          >
            Profile Settings
          </Button>
          <Button
            variant="outline"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </div>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
          <span className="block sm:inline">{error}</span>
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
              <TabsTrigger value="my-resume">My Resume</TabsTrigger>
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

            <TabsContent value="my-resume" className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4">Manage My Resume</h2>
              <textarea
                value={resumeData}
                onChange={(e) => setResumeData(e.target.value)}
                className="w-full h-80 p-3 border border-gray-300 rounded-md mb-4"
              />
              <Button
                onClick={handleUpdateResume}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                Save Resume
              </Button>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Profile Settings Modal */}
      {showProfileSettings && (
        <ProfileSettings 
          isOpen={showProfileSettings}
          onClose={() => setShowProfileSettings(false)}
        />
      )}
    </div>
  )
} 