"use client"

import { useState } from "react"
import { getBrowserInfo } from "@/lib/browser-utils"
import { Copy } from "lucide-react"

interface PdfViewerGuidanceProps {
  className?: string
}

export const PdfViewerGuidance = ({ className = "" }: PdfViewerGuidanceProps) => {
  const browserInfo = getBrowserInfo()
  const [copied, setCopied] = useState(false)
  
  const handleCopyUrl = async () => {
    if (browserInfo.settingsUrl) {
      try {
        await navigator.clipboard.writeText(browserInfo.settingsUrl)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy URL:', err)
      }
    }
  }
  
  return (
    <div className={`text-xs text-amber-600 dark:text-amber-400 ${className}`}>
      <p className="mb-2">
        PDF inline preview isn&apos;t working. You may need to enable it in {browserInfo.name}.
      </p>
      
      {browserInfo.settingsUrl && (
        <div className="space-y-2">
          <p className="font-medium">To enable PDF viewing:</p>
          
          {browserInfo.isBlocked ? (
            // For browsers that block direct links (Chrome, Edge, Opera)
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <code className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-gray-800 dark:text-gray-200 flex-1">
                  {browserInfo.settingsUrl}
                </code>
                <button
                  onClick={handleCopyUrl}
                  className="p-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                  title="Copy URL to clipboard"
                >
                  <Copy className="w-3 h-3" />
                </button>
              </div>
              {copied && (
                <p className="text-green-600 dark:text-green-400 text-xs">
                  URL copied! Paste it in your address bar.
                </p>
              )}
              <p className="text-gray-600 dark:text-gray-400 text-xs leading-relaxed">
                1. Copy the URL above and paste it in a new tab<br/>
                2. {browserInfo.instructions}
              </p>
            </div>
          ) : (
            // For browsers that allow direct links (Firefox)
            <div className="space-y-1">
              <a 
                href={browserInfo.settingsUrl}
                className="inline-block text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 underline font-medium"
                target="_blank"
                rel="noopener noreferrer"
              >
                Open {browserInfo.name} PDF Settings
              </a>
              <p className="text-gray-600 dark:text-gray-400 text-xs">
                {browserInfo.instructions}
              </p>
            </div>
          )}
        </div>
      )}
      
      {!browserInfo.settingsUrl && (
        <div className="space-y-1">
          <p className="font-medium">To enable PDF viewing:</p>
          <p className="text-gray-600 dark:text-gray-400 text-xs leading-relaxed">
            {browserInfo.instructions}
          </p>
        </div>
      )}
    </div>
  )
}