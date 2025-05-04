"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, Upload, CheckCircle, ArrowLeft, Save } from "lucide-react"
import { resume } from "@/lib/api"
import Link from "next/link"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function ProfileSettingsPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [resumeData, setResumeData] = useState<string>("")
  
  // Resume upload states
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Load current resume data
  useEffect(() => {
    fetchResumeData()
  }, [])

  const fetchResumeData = async () => {
    try {
      const data = await resume.getResume()
      if (data && data.resume_content) {
        setResumeData(data.resume_content)
      }
    } catch (err: any) {
      console.error('Failed to load resume:', err)
      setError('Failed to load your current resume. Please try again later.')
    }
  }

  const handleUpdateResume = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await resume.updateResume(resumeData)
      setSuccess('Resume text updated successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to update resume text')
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
    } catch (err: any) {
      setUploadStatus('error')
      setError(err.message || 'Failed to upload resume')
    }
  }

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      <div className="flex items-center mb-6">
        <Link href="/dashboard" className="mr-4">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">Profile Settings</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-6" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative mb-6" role="alert">
          <span className="block sm:inline">{success}</span>
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4">Manage Your Resume</h2>
        <p className="text-sm text-gray-500 mb-4">
          You can edit your resume text directly or upload a new PDF resume.
        </p>
        
        <Tabs defaultValue="edit" className="mt-4">
          <TabsList className="mb-4 w-full">
            <TabsTrigger value="edit" className="flex-1">Edit Resume Text</TabsTrigger>
            <TabsTrigger value="upload" className="flex-1">Upload PDF Resume</TabsTrigger>
          </TabsList>
          
          <TabsContent value="edit" className="space-y-4">
            <div className="border border-gray-200 rounded-md p-2">
              <textarea
                value={resumeData}
                onChange={(e) => setResumeData(e.target.value)}
                className="w-full h-96 p-3 border border-gray-100 rounded-md focus:outline-none focus:ring-1 focus:ring-emerald-500"
                placeholder="Your resume content here..."
              />
            </div>
            
            <div className="flex justify-end">
              <Button 
                onClick={handleUpdateResume}
                disabled={isLoading}
                className="bg-emerald-600 hover:bg-emerald-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="mr-2 h-4 w-4" />
                    Save Resume
                  </>
                )}
              </Button>
            </div>
          </TabsContent>
          
          <TabsContent value="upload" className="space-y-4">
            <div className="border border-gray-200 rounded-md">
              <div className="p-4">
                {uploadStatus === 'success' ? (
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <CheckCircle className="h-8 w-8 text-emerald-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {resumeFile?.name}
                      </p>
                      <p className="text-sm text-emerald-600">
                        Resume uploaded successfully!
                      </p>
                    </div>
                  </div>
                ) : uploadStatus === 'uploading' ? (
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <Loader2 className="h-8 w-8 text-emerald-500 animate-spin" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900">
                        Processing resume...
                      </p>
                      <p className="text-sm text-gray-500">
                        This may take a moment
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="application/pdf"
                      className="hidden"
                      onChange={handleFileChange}
                    />
                    <button
                      type="button"
                      className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-emerald-100 text-emerald-600 mb-3"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="h-8 w-8" />
                    </button>
                    <p className="text-sm text-gray-700">
                      <button 
                        type="button"
                        className="font-medium text-emerald-600 hover:text-emerald-500"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        Click to upload
                      </button> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 mt-1">PDF up to 5MB</p>
                    
                    {resumeFile && (
                      <div className="mt-3">
                        <p className="text-sm font-medium">{resumeFile.name}</p>
                        <Button 
                          type="button" 
                          onClick={handleUploadResume}
                          className="mt-2 bg-emerald-600 hover:bg-emerald-700 text-white"
                          size="sm"
                        >
                          Upload Resume
                        </Button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
            
            <div className="text-sm text-gray-500 mt-2">
              <p>When you upload a new resume, we'll automatically extract the text content for you.</p>
              <p>This will replace your current resume text.</p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Account Settings</h2>
        <p className="text-sm text-gray-500 mb-4">
          Additional settings for your account will appear here.
        </p>
        
        {/* Placeholder for future account settings */}
        <div className="p-4 border border-gray-200 rounded-md bg-gray-50 text-center">
          <p className="text-gray-500">Additional account settings coming soon</p>
        </div>
      </div>
    </div>
  )
} 