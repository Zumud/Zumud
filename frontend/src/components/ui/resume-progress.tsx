"use client"

import { useEffect, useRef, useState } from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

interface ProgressStep {
  id: string
  title: string
  description: string
  duration: number
}

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

const modalSteps: ProgressStep[] = [
  {
    id: "analyzing",
    title: "Reviewing the role",
    description: "Identifying the experience and skills that matter most",
    duration: 8,
  },
  {
    id: "tailoring",
    title: "Tailoring your content",
    description: "Aligning your background with the job requirements",
    duration: 18,
  },
  {
    id: "formatting",
    title: "Refining the structure",
    description: "Improving clarity, hierarchy, and ATS compatibility",
    duration: 10,
  },
  {
    id: "generating",
    title: "Preparing the final document",
    description: "Rendering your resume for download",
    duration: 6,
  },
]

interface ResumeProgressProps {
  isVisible: boolean
  onComplete?: () => void
  onClose?: () => void
}

function StepList({
  steps,
  currentStepIndex,
  isCompleted = false,
}: {
  steps: ProgressStep[]
  currentStepIndex: number
  isCompleted?: boolean
}) {
  return (
    <ol className="space-y-1">
      {steps.map((step, index) => {
        const stepComplete = isCompleted || index < currentStepIndex
        const stepActive = !isCompleted && index === currentStepIndex

        return (
          <li key={step.id} className="relative flex gap-4 py-3">
            {index < steps.length - 1 && (
              <span
                aria-hidden="true"
                className={cn(
                  "absolute left-[9px] top-8 h-[calc(100%-1rem)] w-px",
                  index < currentStepIndex ? "bg-primary/60" : "bg-border"
                )}
              />
            )}
            <span
              aria-hidden="true"
              className={cn(
                "relative mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full border",
                stepComplete && "border-primary bg-primary",
                stepActive && "border-primary bg-background ring-4 ring-primary/10",
                !stepComplete && !stepActive && "border-border bg-background"
              )}
            >
              {stepActive && <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary" />}
              {stepComplete && <span className="h-1.5 w-1.5 rounded-full bg-primary-foreground" />}
            </span>
            <div className="min-w-0">
              <p
                className={cn(
                  "text-sm font-medium",
                  stepActive || stepComplete ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {step.title}
              </p>
              <p className="mt-0.5 text-sm leading-5 text-muted-foreground">
                {step.description}
              </p>
            </div>
          </li>
        )
      })}
    </ol>
  )
}

export default function ResumeProgress({ isVisible, onComplete, onClose }: ResumeProgressProps) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(42)

  useEffect(() => {
    if (!isVisible) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- reset when the modal closes
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

      if (elapsed >= duration) {
        clearInterval(interval)
        onComplete?.()
      }
    }, 500)

    return () => clearInterval(interval)
  }, [isVisible, onComplete])

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isVisible) {
        onClose?.()
      }
    }

    if (isVisible) {
      document.addEventListener("keydown", handleEscape)
      return () => document.removeEventListener("keydown", handleEscape)
    }
  }, [isVisible, onClose])

  const handleBackdropClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (event.target === event.currentTarget) {
      onClose?.()
    }
  }

  if (!isVisible) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/55 p-4 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="relative mx-4 w-full max-w-xl rounded-2xl border border-border bg-background p-6 shadow-2xl sm:p-8">
        {onClose && (
          <button
            onClick={onClose}
            className="absolute right-4 top-4 rounded-lg p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            aria-label="Close progress modal"
          >
            <X className="h-4 w-4" />
          </button>
        )}

        <div className="pr-10">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            Resume generation
          </p>
          <h2 className="mt-2 text-2xl font-semibold tracking-tight text-foreground">
            Preparing your resume
          </h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            We are tailoring the content and formatting it for this role. This usually takes less than a minute.
          </p>
        </div>

        <div className="mt-7">
          <div className="mb-2 flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium tabular-nums text-foreground">{Math.round(progress)}%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-[width] duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="mt-6 border-t border-border pt-3">
          <StepList steps={modalSteps} currentStepIndex={currentStepIndex} />
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-border pt-5 text-sm text-muted-foreground">
          <span>Keep this window open while the document is prepared.</span>
          <span className="shrink-0 pl-4 tabular-nums">About {timeRemaining}s</span>
        </div>
      </div>
    </div>
  )
}

export type GenerationProgressKind = "resume" | "cover-letter" | "answer"

interface InlineProgressConfig {
  label: string
  heading: string
  description: string
  steps: ProgressStep[]
}

const inlineProgressConfig: Record<GenerationProgressKind, InlineProgressConfig> = {
  resume: {
    label: "Resume generation",
    heading: "Preparing your resume",
    description: "Tailoring the content and formatting it for this role.",
    steps: [
      {
        id: "analyzing",
        title: "Review role",
        description: "Identify priorities and required experience",
        duration: 8,
      },
      {
        id: "tailoring",
        title: "Tailor content",
        description: "Align your resume with the role",
        duration: 12,
      },
      {
        id: "formatting",
        title: "Refine structure",
        description: "Improve clarity and ATS compatibility",
        duration: 8,
      },
      {
        id: "generating",
        title: "Prepare document",
        description: "Render the final resume",
        duration: 2,
      },
    ],
  },
  "cover-letter": {
    label: "Cover letter generation",
    heading: "Preparing your cover letter",
    description: "Connecting your experience to the role in a focused letter.",
    steps: [
      {
        id: "analyzing",
        title: "Review role",
        description: "Identify the employer's main priorities",
        duration: 7,
      },
      {
        id: "matching",
        title: "Match experience",
        description: "Select the strongest evidence from your background",
        duration: 10,
      },
      {
        id: "drafting",
        title: "Draft letter",
        description: "Build a clear and specific narrative",
        duration: 10,
      },
      {
        id: "refining",
        title: "Polish wording",
        description: "Check tone, clarity, and structure",
        duration: 3,
      },
    ],
  },
  answer: {
    label: "Answer generation",
    heading: "Preparing your answer",
    description: "Building a direct answer around the role and your experience.",
    steps: [
      {
        id: "analyzing",
        title: "Read question",
        description: "Determine what the employer is asking for",
        duration: 6,
      },
      {
        id: "matching",
        title: "Find evidence",
        description: "Choose relevant details from your experience",
        duration: 8,
      },
      {
        id: "drafting",
        title: "Draft answer",
        description: "Write a focused and natural response",
        duration: 8,
      },
      {
        id: "refining",
        title: "Final review",
        description: "Improve clarity and remove repetition",
        duration: 3,
      },
    ],
  },
}

interface InlineGenerationProgressProps {
  kind: GenerationProgressKind
  onComplete?: () => void
  isComplete?: boolean
}

export function InlineGenerationProgress({
  kind,
  onComplete,
  isComplete,
}: InlineGenerationProgressProps) {
  const config = inlineProgressConfig[kind]
  const duration = totalDuration(config.steps)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [progress, setProgress] = useState(0)
  const [timeRemaining, setTimeRemaining] = useState(duration)
  const [isWaitingForBackend, setIsWaitingForBackend] = useState(false)
  const [isCompleted, setIsCompleted] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const onCompleteRef = useRef(onComplete)

  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  useEffect(() => {
    let elapsed = 0

    intervalRef.current = setInterval(() => {
      elapsed += 0.5
      setCurrentStepIndex(stepIndexAt(elapsed, config.steps))

      if (elapsed >= duration) {
        setProgress(95)
        setIsWaitingForBackend(true)
        setTimeRemaining(0)
      } else {
        setProgress((elapsed / duration) * 100)
        setTimeRemaining(Math.ceil(duration - elapsed))
      }
    }, 500)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [config.steps, duration])

  useEffect(() => {
    if (!isComplete || isCompleted) return

    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // eslint-disable-next-line react-hooks/set-state-in-effect -- the completed request drives the progress state
    setIsCompleted(true)
    setCurrentStepIndex(config.steps.length - 1)
    setProgress(100)
    setTimeRemaining(0)
    setIsWaitingForBackend(false)
  }, [config.steps.length, isComplete, isCompleted])

  useEffect(() => {
    if (!isCompleted) return

    const timeout = setTimeout(() => onCompleteRef.current?.(), 500)
    return () => clearTimeout(timeout)
  }, [isCompleted])

  const statusText = isCompleted
    ? "Ready"
    : isWaitingForBackend
      ? "Finalizing"
      : `About ${timeRemaining}s remaining`

  return (
    <section
      className="rounded-2xl border border-border bg-card p-5 shadow-sm sm:p-6"
      aria-live="polite"
      aria-label={`${config.label} progress`}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
            {config.label}
          </p>
          <h3 className="mt-1.5 text-lg font-semibold tracking-tight text-card-foreground">
            {config.heading}
          </h3>
          <p className="mt-1 text-sm text-muted-foreground">
            {config.description}
          </p>
        </div>
        <div className="flex items-baseline gap-2 sm:block sm:text-right">
          <span className="text-lg font-semibold tabular-nums text-card-foreground">
            {Math.round(progress)}%
          </span>
          <p className="text-xs text-muted-foreground sm:mt-1">{statusText}</p>
        </div>
      </div>

      <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="mt-3 text-sm text-muted-foreground">
        <span className="font-medium text-card-foreground">
          {isCompleted ? "Complete" : `Current step: ${config.steps[currentStepIndex].title}`}
        </span>
        {!isCompleted && ` — ${config.steps[currentStepIndex].description}`}
      </p>

      <ol className="mt-6 grid gap-3 sm:grid-cols-4">
        {config.steps.map((step, index) => {
          const stepComplete = isCompleted || index < currentStepIndex
          const stepActive = !isCompleted && index === currentStepIndex

          return (
            <li key={step.id} className="flex min-w-0 items-center gap-2">
              <span
                className={cn(
                  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11px] font-semibold tabular-nums",
                  stepComplete && "border-primary bg-primary text-primary-foreground",
                  stepActive && "border-primary text-primary",
                  !stepComplete && !stepActive && "border-border text-muted-foreground"
                )}
              >
                {index + 1}
              </span>
              <span
                className={cn(
                  "min-w-0 text-xs font-medium",
                  stepComplete || stepActive ? "text-card-foreground" : "text-muted-foreground"
                )}
              >
                {step.title}
              </span>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
