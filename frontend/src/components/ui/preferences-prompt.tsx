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

  const handleSavePreference = async () => {
    setIsLoading(true)
    try {
      const preference = `Apply edits like: "${editInstruction}" to future resumes`
      await onSavePreference(preference)
      onDismiss()
    } catch (error) {
      console.error('Failed to save preference:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!isVisible) return null

  return (
    <div className="bg-gradient-to-r from-emerald-50 to-blue-50 border border-emerald-200 rounded-lg p-3 mb-3 mx-3 animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center flex-1">
          <div className="bg-emerald-100 p-1.5 rounded-full mr-3 flex-shrink-0">
            <Sparkles className="h-4 w-4 text-emerald-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-900">
                Save as preference?
              </h3>
              <button 
                onClick={onDismiss}
                className="text-gray-400 hover:text-gray-600 transition-colors p-1 ml-2 flex-shrink-0"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <p className="text-xs text-gray-600 mb-2">
              Apply "<span className="font-medium text-emerald-700">{editInstruction}</span>" to future resumes automatically?
            </p>
            
            <div className="flex items-center space-x-2">
              <Button
                onClick={handleSavePreference}
                disabled={isLoading}
                size="sm"
                className="bg-emerald-600 hover:bg-emerald-700 text-xs px-3 py-1.5 h-7"
              >
                {isLoading ? 'Saving...' : 'Yes, Save'}
              </Button>
              <Button
                onClick={onDismiss}
                disabled={isLoading}
                variant="ghost"
                size="sm"
                className="text-xs px-3 py-1.5 h-7 text-gray-600 hover:text-gray-800"
              >
                No, Skip
              </Button>
              <span className="text-xs text-gray-400 ml-auto">
                Auto-dismisses in {countdown}s
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 