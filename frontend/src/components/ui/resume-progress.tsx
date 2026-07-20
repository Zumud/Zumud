"use client"

import { useEffect, useState, useRef } from "react"
import { CheckCircle, Clock, FileText, Sparkles, Zap, X, Loader2 } from "lucide-react"

interface ProgressStep {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  duration: number // in seconds
}

// Which step is active after `elapsed` seconds of the scripted timeline.
function stepIndexAt(elapsed: number, steps: ProgressStep[]): number {
  let stepStart = 0
  for (let i = 0; i < steps.length; i++) {
    if (elapsed <= stepStart + steps[i].duration) {
      return i
    }
    stepStart += steps[i].duration
  }
  return steps.length - 1
}

const totalDuration = (steps: ProgressStep[]) =>
  steps.reduce((sum, step) => sum + step.duration, 0)

// ---------------------------------------------------------------------------
// Modal variant (landing-page anonymous flow): scripted timeline that
// self-completes when the timer runs out.
// ---------------------------------------------------------------------------

const modalSteps: ProgressStep[] = [
  {
    id: "analyzing",
    title: "Analyzing Job Requirements",
    description: "Understanding key skills and qualifications needed",
    icon: <Sparkles className="h-5 w-5" />,
    duration: 8
  },
  {
    id: "tailoring",
    title: "Tailoring Your Experience",
    description: "Matching your background to job requirements",
    icon: <Zap className="h-5 w-5" />,
    duration: 18
  },
  {
    id: "formatting",
    title: "Optimizing Layout & Format",
    description: "Creating ATS-friendly professional layout",
    icon: <FileText className="h-5 w-5" />,
    duration: 10
  },
  {
    id: "generating",
    title: "Generating Your PDF",
    description: "Finalizing your tailored resume",
    icon: <CheckCircle className="h-5 w-5" />,
    duration: 6
  }
]

interface ResumeProgressProps {
  isVisible: boolean
  onComplete?: () => void
  onClose?: () => void
}

export default function ResumeProgress({ isVisible, onComplete, onClose }: ResumeProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(42)

  useEffect(() => {
    if (!isVisible) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: refactor to key-based reset
      setCurrentStepIndex(0)
      setProgress(0)
      setTimeRemaining(42)
      return
    }

    const duration = totalDuration(modalSteps)
    let elapsed = 0

    const interval = setInterval(() => {
      elapsed += 0.5

      setCurrentStepIndex(stepIndexAt(elapsed, modalSteps))
      setProgress(Math.min((elapsed / duration) * 100, 100))
      setTimeRemaining(Math.ceil(Math.max(duration - elapsed, 0)))

      // Complete when done
      if (elapsed >= duration) {
        clearInterval(interval)
        onComplete?.()
      }
    }, 500)

    return () => clearInterval(interval)
  }, [isVisible, onComplete])

  // Add escape key functionality
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isVisible) {
        onClose?.()
      }
    }

    if (isVisible) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [isVisible, onClose])

  // Handle backdrop click
  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose?.()
    }
  }

  if (!isVisible) return null

  return (
    <div 
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-white dark:bg-gray-900 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-2xl w-full mx-4 relative">
        {/* Close button */}
        {onClose && (
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200 group"
            aria-label="Close progress modal"
          >
            <X className="h-5 w-5 text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200" />
          </button>
        )}

        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-violet-500 rounded-full mb-4">
            <Sparkles className="h-8 w-8 text-white animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">
            Crafting Your Perfect Resume
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Our AI is personalizing your resume for maximum impact
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Overall Progress
            </span>
            <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
              {Math.round(progress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-4 mb-8">
          {modalSteps.map((step, index) => {
            const isActive = index === currentStepIndex
            const isCompleted = index < currentStepIndex
            
            return (
              <div 
                key={step.id}
                className={`flex items-start space-x-4 p-4 rounded-xl transition-all duration-300 ${
                  isActive 
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-700' 
                    : isCompleted
                    ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700'
                    : 'bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isCompleted
                    ? 'bg-green-500 text-white'
                    : isActive
                    ? 'bg-blue-500 text-white animate-pulse'
                    : 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : isActive ? (
                    <div className="flex space-x-1">
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1 h-1 bg-white rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  ) : (
                    step.icon
                  )}
                </div>
                <div className="flex-grow">
                  <h3 className={`font-semibold transition-colors duration-300 ${
                    isActive 
                      ? 'text-blue-700 dark:text-blue-300' 
                      : isCompleted
                      ? 'text-green-700 dark:text-green-300'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    {step.title}
                  </h3>
                  <p className={`text-sm mt-1 transition-colors duration-300 ${
                    isActive 
                      ? 'text-blue-600 dark:text-blue-400' 
                      : isCompleted
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-gray-500 dark:text-gray-500'
                  }`}>
                    {step.description}
                  </p>
                </div>
                {isActive && (
                  <div className="flex-shrink-0">
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-500 border-t-transparent"></div>
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Time Remaining */}
        <div className="text-center">
          <div className="inline-flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-full px-4 py-2">
            <Clock className="h-4 w-4 text-gray-500 dark:text-gray-400" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              About {timeRemaining} seconds remaining
            </span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-3">
            ✨ Creating a resume that gets you noticed
          </p>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Inline variant (dashboard): scripted timeline that caps at 95% and waits
// for the backend response (`forceComplete`) before showing 100%.
// ---------------------------------------------------------------------------

const inlineSteps: ProgressStep[] = [
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

interface InlineResumeProgressProps {
  isVisible: boolean
  onComplete?: () => void
  forceComplete?: boolean // Backend response triggers completion externally
}

export function InlineResumeProgress({ isVisible, onComplete, forceComplete }: InlineResumeProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(30)
  const [isWaitingForBackend, setIsWaitingForBackend] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!isVisible) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: refactor to key-based reset
      setCurrentStepIndex(0)
      setProgress(0)
      setTimeRemaining(30)
      setIsWaitingForBackend(false)
      setIsCompleted(false)
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }

    // Don't start timer if already completed
    if (isCompleted) {
      return
    }

    const duration = totalDuration(inlineSteps)
    let elapsed = 0

    intervalRef.current = setInterval(() => {
      // Stop updating if we're completed
      if (isCompleted) {
        return
      }

      elapsed += 0.5

      setCurrentStepIndex(stepIndexAt(elapsed, inlineSteps))

      // Calculate overall progress - cap at 95% when waiting for backend
      let newProgress = (elapsed / duration) * 100
      if (elapsed >= duration) {
        newProgress = 95 // Don't show 100% until backend responds
        setIsWaitingForBackend(true)
        setTimeRemaining(0)
      } else {
        setProgress(newProgress)
        setTimeRemaining(Math.ceil(Math.max(duration - elapsed, 0)))
      }

      if (!isWaitingForBackend && !isCompleted) {
        setProgress(newProgress)
      }
    }, 500)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isVisible, isCompleted])

  // Handle external completion trigger
  useEffect(() => {
    if (forceComplete && (isWaitingForBackend || progress > 0) && !isCompleted) {
      // Clear the timer immediately to prevent further updates
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }

      // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: refactor to key-based reset
      setIsCompleted(true)
      setProgress(100)
      setTimeout(() => {
        onComplete?.()
      }, 500) // Small delay to show 100% completion
    }
  }, [forceComplete, isWaitingForBackend, progress, isCompleted, onComplete])

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
            {isCompleted
              ? "Complete!"
              : isWaitingForBackend 
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
        {inlineSteps.map((step, index) => {
          const isActive = index === currentStepIndex && !isCompleted
          const isStepCompleted = index < currentStepIndex || (index === currentStepIndex && isCompleted)
          const isFinalStepWaiting = isActive && index === inlineSteps.length - 1 && isWaitingForBackend
          
          if (!isActive && !isStepCompleted) return null
          
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
                isStepCompleted
                  ? 'bg-green-500 text-white'
                  : 'bg-blue-500 text-white'
              }`}>
                {isStepCompleted ? (
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
          {isCompleted
            ? "🎉 Your tailored resume is ready!"
            : isWaitingForBackend 
            ? "🔥 Your tailored resume is almost ready!"
            : "✨ Creating a resume that gets you noticed"
          }
        </p>
      </div>
    </div>
  )
}
