"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { getUserData, removeAccessToken, removeUserData } from "@/lib/utils"
import { resume, applications } from "@/lib/api"
import PdfViewer from "@/components/pdf-viewer"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Check, Download, Loader2 } from "lucide-react"
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
  const [latexCode, setLatexCode] = useState<string>("")
  const [error, setError] = useState<string | null>(null)
  const [showProfileSettings, setShowProfileSettings] = useState(false)

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
      const result = await applications.generateResume(jobDescription)
      
      if (result && result.source && result.source.latex_code) {
        setLatexCode(result.source.latex_code)
      }
      
      if (result && result.access && result.access.local_path) {
        // Convert the blob to a data URL for the PDF viewer
        const pdfBlob = new Blob([result], { type: 'application/pdf' })
        const pdfUrl = URL.createObjectURL(pdfBlob)
        setGeneratedResumePdf(pdfUrl)
      }
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
      link.download = "tailored-resume.pdf"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
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
                  <Button
                    onClick={handleDownloadResume}
                    className="mt-4 bg-emerald-600 hover:bg-emerald-700"
                  >
                    <Download className="mr-2 h-4 w-4" />
                    Download Resume
                  </Button>
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
                <div className="mt-4 border border-gray-200 rounded-md p-4 bg-gray-50">
                  <textarea
                    value={coverLetter}
                    onChange={(e) => setCoverLetter(e.target.value)}
                    className="w-full h-80 p-3 border border-gray-300 rounded-md"
                    readOnly={false}
                  />
                </div>
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