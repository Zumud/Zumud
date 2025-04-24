"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Loader2 } from "lucide-react"
import { resume } from "@/lib/api"

// AI model and resume template options
const AI_MODELS = ['GPT_3_5_TURBO', 'GPT_4', 'GPT_4_TURBO', 'CLAUDE_OPUS'];
const RESUME_TEMPLATES = ['MINIMAL', 'PROFESSIONAL', 'MODERN', 'ACADEMIC', 'CREATIVE'];

interface ProfileSettingsProps {
  isOpen: boolean
  onClose: () => void
}

export default function ProfileSettings({ isOpen, onClose }: ProfileSettingsProps) {
  const [selectedAiModel, setSelectedAiModel] = useState<string>(AI_MODELS[0])
  const [selectedResumeTemplate, setSelectedResumeTemplate] = useState<string>(RESUME_TEMPLATES[1])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Load current settings
  useEffect(() => {
    async function loadSettings() {
      try {
        // You'd need to create this API endpoint to get the current settings
        const settings = await resume.getTailoringOptions()
        if (settings) {
          setSelectedAiModel(settings.ai_model || AI_MODELS[0])
          setSelectedResumeTemplate(settings.resume_template || RESUME_TEMPLATES[1])
        }
      } catch (err) {
        // If settings don't exist yet, no need to show an error
        console.log('Could not load settings, using defaults')
      }
    }

    if (isOpen) {
      loadSettings()
    }
  }, [isOpen])

  const handleSaveSettings = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)

    try {
      await resume.updateTailoringOptions(selectedAiModel, selectedResumeTemplate)
      setSuccess('Settings updated successfully!')
    } catch (err: any) {
      setError(err.message || 'Failed to update settings')
    } finally {
      setIsLoading(false)
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

        <div className="space-y-4">
          <div>
            <label htmlFor="ai-model" className="block text-sm font-medium text-gray-700 mb-1">
              AI Model
            </label>
            <select
              id="ai-model"
              value={selectedAiModel}
              onChange={(e) => setSelectedAiModel(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm rounded-md"
            >
              {AI_MODELS.map((model) => (
                <option key={model} value={model}>
                  {model.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Select the AI model to use for generating content
            </p>
          </div>

          <div>
            <label htmlFor="resume-template" className="block text-sm font-medium text-gray-700 mb-1">
              Resume Template
            </label>
            <select
              id="resume-template"
              value={selectedResumeTemplate}
              onChange={(e) => setSelectedResumeTemplate(e.target.value)}
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm rounded-md"
            >
              {RESUME_TEMPLATES.map((template) => (
                <option key={template} value={template}>
                  {template.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-gray-500">
              Choose the style for your generated resumes
            </p>
          </div>

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