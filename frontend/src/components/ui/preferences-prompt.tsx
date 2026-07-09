'use client'

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { X, Sparkles } from 'lucide-react'

interface PreferencesPromptProps {
  isVisible: boolean
  editInstruction: string
  onSavePreference: (preference: string) => Promise<void>
  onDismiss: () => void
}

export default function PreferencesPrompt({ 
  isVisible, 
  editInstruction, 
  onSavePreference, 
  onDismiss 
}: PreferencesPromptProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [countdown, setCountdown] = useState(15)

  // Auto-dismiss countdown
  useEffect(() => {
    if (!isVisible) {
      setCountdown(15)
      return
    }

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          onDismiss()
          return 15
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isVisible, onDismiss])

  const handleSavePreference = () => {
    // Immediate visual feedback
    setIsLoading(true)
    setIsSaved(true)
    
    // Fire the preference save immediately - completely independent operation
    const preference = `Apply edits like: "${editInstruction}" to future resumes`
    
    // Start the API call immediately in the background
    onSavePreference(preference).then(() => {
      console.log('Preference saved successfully!')
    }).catch((error) => {
      console.error('Failed to save preference:', error)
      // On error, revert the visual state
      setIsSaved(false)
      setIsLoading(false)
      return // Don't dismiss on error
    })
    
    // Dismiss after showing success for a brief moment
    setTimeout(() => {
      onDismiss()
    }, 1500)
  }

  if (!isVisible) return null

  return (
    <div className="bg-brand-gradient-soft mx-3 mb-3 rounded-xl border border-brand/20 p-3 animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="flex items-start justify-between mb-2">
        <div className="flex flex-1 items-center">
          <div className="mr-3 flex-shrink-0 rounded-full bg-brand/15 p-1.5">
            <Sparkles className="h-4 w-4 text-brand" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium">
                Save as preference?
              </h3>
              <button
                onClick={onDismiss}
                className="ml-2 flex-shrink-0 p-1 text-muted-foreground transition-colors hover:text-foreground"
                aria-label="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="mb-2 text-xs text-muted-foreground">
              <span className="font-medium text-brand">Your edit is already being applied!</span> Would you also like to save &quot;<span className="font-medium text-foreground">{editInstruction}</span>&quot; as a preference for future resumes?
            </p>

            <div className="flex items-center space-x-2">
              <Button
                onClick={handleSavePreference}
                disabled={isLoading || isSaved}
                variant="brand"
                size="sm"
                className="h-7 px-3 text-xs"
              >
                {isSaved ? 'Saved!' : isLoading ? 'Saving...' : 'Yes, save'}
              </Button>
              <Button
                onClick={onDismiss}
                disabled={isLoading}
                variant="ghost"
                size="sm"
                className="h-7 px-3 text-xs"
              >
                No, skip
              </Button>
              <span className="ml-auto text-xs text-muted-foreground">
                Auto-dismisses in {countdown}s
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 