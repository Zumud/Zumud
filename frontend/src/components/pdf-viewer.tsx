"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ExternalLink } from "lucide-react"
import { PdfViewerGuidance } from "@/components/ui/pdf-viewer-guidance"

interface PdfViewerProps {
  pdfUrl: string
}

// Mobile detection utility
const isMobileDevice = () => {
  if (typeof window === 'undefined') return false
  
  const userAgent = window.navigator.userAgent.toLowerCase()
  const mobileKeywords = ['android', 'webos', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
  
  return mobileKeywords.some(keyword => userAgent.includes(keyword)) || 
         window.innerWidth < 768 ||
         ('ontouchstart' in window)
}

// iOS detection specifically (worst PDF support)
const isIOS = () => {
  if (typeof window === 'undefined') return false
  return /iPad|iPhone|iPod/.test(window.navigator.userAgent)
}



export default function PdfViewer({ pdfUrl }: PdfViewerProps) {
  const [isMounted, setIsMounted] = useState(false)
  const [isMobile, setIsMobile] = useState(false)
  const [showIframe, setShowIframe] = useState(false)
  const [iframeError, setIframeError] = useState(false)

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- pre-gate debt: hydration mount-gate pattern
    setIsMounted(true)
    setIsMobile(isMobileDevice())
    
    // On mobile, we'll start with buttons, on desktop try iframe first
    if (!isMobileDevice()) {
      setShowIframe(true)
    }
  }, [])

  const handleOpenInNewTab = () => {
    window.open(pdfUrl, '_blank', 'noopener,noreferrer')
  }

  const handleIframeError = () => {
    setIframeError(true)
    setShowIframe(false)
  }

  if (!isMounted) {
    return (
      <div
        className="h-[400px] md:h-[500px] w-full bg-muted animate-pulse rounded-lg"
        aria-label="Loading PDF viewer"
        role="status"
      >
        <span className="sr-only">Loading PDF viewer...</span>
      </div>
    )
  }

  // Mobile-first approach: Show action buttons primarily
  if (isMobile || iframeError || !showIframe) {
    return (
      <section aria-labelledby="pdf-viewer-title" className="w-full">
        <h2 id="pdf-viewer-title" className="sr-only">Your Interview-Ready Resume</h2>
        
        <div className="w-full min-h-[300px] md:min-h-[400px] border border-border rounded-lg overflow-hidden shadow-sm bg-muted/40">
          <div className="flex flex-col items-center justify-center h-full p-8 text-center space-y-6">
            {/* PDF Icon */}
            <div className="w-20 h-20 md:w-24 md:h-24 bg-destructive/10 rounded-2xl flex items-center justify-center">
              <svg className="w-10 h-10 md:w-12 md:h-12 text-destructive" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
            </div>

            {/* Message */}
            <div className="space-y-2">
              <h3 className="text-lg md:text-xl font-semibold">
                Your PDF is ready
              </h3>
              <p className="text-sm md:text-base text-muted-foreground max-w-md">
                {isMobile ?
                  "Your browser doesn't support inline PDF preview. Tap below to view your resume." :
                  "Choose how you'd like to view your PDF document."
                }
              </p>
            </div>

            {/* Action Button */}
            <div className="w-full max-w-md">
              <Button
                onClick={handleOpenInNewTab}
                variant="brand"
                className="w-full font-semibold"
                size="lg"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Open PDF
              </Button>
            </div>

            {/* Error message if iframe failed */}
            {iframeError && (
              <PdfViewerGuidance className="mt-2 max-w-md" />
            )}
          </div>
        </div>
      </section>
    )
  }

  // Desktop iframe approach (with error handling)
  return (
    <section aria-labelledby="pdf-viewer-title" className="w-full">
      <h2 id="pdf-viewer-title" className="sr-only">Your Interview-Ready Resume</h2>
      <div className="w-full h-[70vh] min-h-[400px] max-h-[800px] md:h-[600px] border border-border rounded-lg overflow-hidden shadow-sm">
        <iframe 
          src={`${pdfUrl}#toolbar=0&view=FitH`} 
          className="w-full h-full" 
          title="Your Interview-Ready Resume" 
          aria-label="PDF preview of your interview-ready resume"
          loading="lazy"
          onError={handleIframeError}
          onLoad={(e) => {
            // Check if iframe content loaded successfully
            const iframe = e.target as HTMLIFrameElement
            try {
              // If we can't access the content or if it's empty, show fallback
              setTimeout(() => {
                if (!iframe.contentDocument || iframe.contentDocument.body?.children.length === 0) {
                  handleIframeError()
                }
              }, 2000)
            } catch {
              // Cross-origin error means the PDF might be loading, so we'll let it be
            }
          }}
        />
      </div>
      
      {/* Fallback button for desktop */}
      <div className="mt-4 flex justify-center">
        <Button
          onClick={handleOpenInNewTab}
          variant="ghost"
          size="sm"
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-xs"
        >
          <ExternalLink className="w-3 h-3 mr-1" />
          Open in New Tab
        </Button>
      </div>
    </section>
  )
}
