"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Loader2, Upload, CheckCircle } from "lucide-react"
import { resume } from "@/lib/api"

// AI model and resume template options have been removed

interface ProfileSettingsProps {
  isOpen: boolean
  onClose: () => void
}

export default function ProfileSettings({ isOpen, onClose }: ProfileSettingsProps) {
  // Removed state variables for AI model and resume template
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Resume upload states
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Load current settings - removed as we don't need to load AI model and resume template
  
  const handleSaveSettings = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      // We're not sending AI model and resume template anymore
      setSuccess('Settings updated successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to update settings')
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
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Profile Settings</DialogTitle>
        </DialogHeader>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline">{success}</span>
          </div>
        )}

        <div className="space-y-6">
          {/* Resume upload section */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-1">Update Your Resume</h3>
            <p className="text-xs text-gray-500 mb-2">
              Upload a new resume to update your profile. We'll extract the text automatically.
            </p>
            
            <div className="mt-2 border border-gray-200 rounded-md">
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
                      <p className="text-xs text-emerald-600">
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
                      <p className="text-xs text-gray-500">
                        This may take a moment
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4">
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="application/pdf"
                      className="hidden"
                      onChange={handleFileChange}
                    />
                    <button
                      type="button"
                      className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-emerald-100 text-emerald-600 mb-3"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload className="h-6 w-6" />
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
                          className="mt-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm py-1"
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
          </div>

          {/* Removed AI Model and Resume Template sections */}

          <div className="flex justify-end pt-4">
            <Button 
              type="button" 
              variant="outline" 
              onClick={onClose} 
              className="mr-2"
            >
              Cancel
            </Button>
            <Button 
              type="button" 
              onClick={handleSaveSettings} 
              disabled={isLoading}
              className="bg-emerald-600 hover:bg-emerald-700"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                "Save Settings"
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 