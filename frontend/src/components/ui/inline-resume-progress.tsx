"use client"

import { useEffect, useState } from "react"
import { CheckCircle, Clock, FileText, Sparkles, Zap, Loader2 } from "lucide-react"

interface InlineResumeProgressProps {
  isVisible: boolean
  onComplete?: () => void
  forceComplete?: boolean // New prop to trigger completion externally
}

interface ProgressStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  duration: number // in seconds
}

const progressSteps: ProgressStep[] = [
  {
    id: "analyzing",
    title: "Analyzing Job Requirements",
    description: "Understanding key skills and qualifications",
    icon: <Sparkles className="h-3 w-3" />,
    duration: 8
  },
  {
    id: "tailoring",
    title: "Tailoring Your Experience",
    description: "Matching your background to job requirements",
    icon: <Zap className="h-3 w-3" />,
    duration: 12
  },
  {
    id: "formatting",
    title: "Optimizing Layout & Format",
    description: "Creating ATS-friendly professional layout",
    icon: <FileText className="h-3 w-3" />,
    duration: 8
  },
  {
    id: "generating",
    title: "Finalizing Your Resume",
    description: "Applying finishing touches and quality checks",
    icon: <CheckCircle className="h-3 w-3" />,
    duration: 2
  }
]

export default function InlineResumeProgress({ isVisible, onComplete, forceComplete }: InlineResumeProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(30)
  const [isWaitingForBackend, setIsWaitingForBackend] = useState(false)

  useEffect(() => {
    if (!isVisible) {
      setCurrentStepIndex(0)
      setProgress(0)
      setTimeRemaining(30)
      setIsWaitingForBackend(false)
      return
    }

    const totalDuration = progressSteps.reduce((sum, step) => sum + step.duration, 0)
    let elapsed = 0
    
    const interval = setInterval(() => {
      elapsed += 0.5
      
      // Calculate which step we're in
      let stepStart = 0
      let newStepIndex = 0
      
      for (let i = 0; i < progressSteps.length; i++) {
        if (elapsed <= stepStart + progressSteps[i].duration) {
          newStepIndex = i
          break
        }
        stepStart += progressSteps[i].duration
        if (i === progressSteps.length - 1) {
          newStepIndex = i
        }
      }
      
      setCurrentStepIndex(newStepIndex)
      
      // Calculate overall progress - cap at 95% when waiting for backend
      let newProgress = (elapsed / totalDuration) * 100
      if (elapsed >= totalDuration) {
        newProgress = 95 // Don't show 100% until backend responds
        setIsWaitingForBackend(true)
        setTimeRemaining(0)
      } else {
        setProgress(newProgress)
        // Calculate time remaining
        const remaining = Math.max(totalDuration - elapsed, 0)
        setTimeRemaining(Math.ceil(remaining))
      }
      
      if (!isWaitingForBackend) {
        setProgress(newProgress)
      }
      
      // Don't auto-complete - let the backend response trigger completion
      if (elapsed >= totalDuration && !isWaitingForBackend) {
        setIsWaitingForBackend(true)
      }
    }, 500)

    return () => clearInterval(interval)
  }, [isVisible, onComplete])

  // Handle external completion trigger
  useEffect(() => {
    if (forceComplete && isWaitingForBackend) {
      setProgress(100)
      setTimeout(() => {
        onComplete?.()
      }, 500) // Small delay to show 100% completion
    }
  }, [forceComplete, isWaitingForBackend, onComplete])

  if (!isVisible) return null

  return (
    <div className="bg-gradient-to-br from-blue-50/50 to-violet-50/50 dark:from-blue-900/10 dark:to-violet-900/10 rounded-xl border border-blue-200/50 dark:border-blue-700/50 p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-500 to-violet-500 rounded-full">
            <Sparkles className="h-4 w-4 text-white animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-gray-800 dark:text-white">
              Generating Your Resume
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              AI is crafting your personalized resume
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm font-medium text-blue-600 dark:text-blue-400">
            {Math.round(progress)}%
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <Clock className="h-3 w-3 mr-1" />
            {isWaitingForBackend 
              ? "Almost ready..."
              : `~${timeRemaining}s`
            }
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

              {/* Current Step */}
        <div className="space-y-2">
          {progressSteps.map((step, index) => {
            const isActive = index === currentStepIndex
            const isCompleted = index < currentStepIndex
            const isFinalStepWaiting = isActive && index === progressSteps.length - 1 && isWaitingForBackend
            
            if (!isActive && !isCompleted) return null
            
            return (
              <div 
                key={step.id}
                className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 ${
                  isActive 
                    ? 'bg-blue-100/50 dark:bg-blue-900/20' 
                    : 'bg-green-100/50 dark:bg-green-900/20'
                }`}
              >
                <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isCompleted
                    ? 'bg-green-500 text-white'
                    : 'bg-blue-500 text-white'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="h-3 w-3" />
                  ) : isActive ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    step.icon
                  )}
                </div>
                <div className="flex-grow">
                  <h4 className={`font-medium text-xs transition-colors duration-300 ${
                    isActive 
                      ? 'text-blue-700 dark:text-blue-300' 
                      : 'text-green-700 dark:text-green-300'
                  }`}>
                    {isFinalStepWaiting ? "Processing Final Details" : step.title}
                  </h4>
                  <p className={`text-xs mt-0.5 transition-colors duration-300 ${
                    isActive 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : 'text-green-600 dark:text-green-400'
                  }`}>
                    {isFinalStepWaiting ? "Almost ready! Compiling your perfect resume..." : step.description}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

      {/* Footer */}
      <div className="mt-3 text-center">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {isWaitingForBackend 
            ? "🔥 Your tailored resume is almost ready!"
            : "✨ Creating a resume that gets you noticed"
          }
        </p>
      </div>
    </div>
  )
} 