"use client"

import { useState, useEffect } from "react"

interface PdfViewerProps {
  pdfUrl: string
}

export default function PdfViewer({ pdfUrl }: PdfViewerProps) {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setIsMounted(true)
  }, [])

  if (!isMounted) {
    return (
      <div 
        className="h-[500px] w-full bg-gray-100 animate-pulse rounded-lg" 
        aria-label="Loading PDF viewer"
        role="status"
      >
        <span className="sr-only">Loading PDF viewer...</span>
      </div>
    )
  }

  return (
    <section aria-labelledby="pdf-viewer-title" className="w-full">
      <h2 id="pdf-viewer-title" className="sr-only">Improved Resume Preview</h2>
      <div className="w-full h-[600px] border border-gray-200 rounded-lg overflow-hidden shadow-md">
        <iframe 
          src={`${pdfUrl}#toolbar=0`} 
          className="w-full h-full" 
          title="Improved Resume Preview" 
          aria-label="PDF preview of your improved resume"
          loading="lazy"
        />
      </div>
    </section>
  )
}
