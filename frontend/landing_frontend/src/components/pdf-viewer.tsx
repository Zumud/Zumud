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
    return <div className="h-[500px] w-full bg-gray-100 animate-pulse rounded-lg"></div>
  }

  return (
    <div className="w-full h-[600px] border border-gray-200 rounded-lg overflow-hidden shadow-md">
      <iframe src={`${pdfUrl}#toolbar=0`} className="w-full h-full" title="Improved Resume Preview" />
    </div>
  )
}
