"use client"

import type React from "react"

import { useState } from "react"
import { Check, Upload, Download, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import PdfViewer from "./pdf-viewer"

export default function ResumeImprover() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [improvedResumePdf, setImprovedResumePdf] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile)
      setError(null)
    } else {
      setFile(null)
      setError("Please select a valid PDF file")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/applications/resume/improve', true);
      xhr.responseType = 'blob';
      xhr.timeout = 300000; // Set timeout to 5 minutes (300000ms)
      
      xhr.onload = function() {
        if (xhr.status === 200) {
          const blob = xhr.response;
          const pdfUrl = URL.createObjectURL(blob);
          setImprovedResumePdf(pdfUrl);
          setIsModalOpen(false);
        } else {
          console.error('XHR error:', xhr.status);
          setError("Failed to improve resume. Please try again.");
        }
        setIsUploading(false);
      };
      
      xhr.onerror = function() {
        console.error('XHR network error');
        setError("Network error. Please try again.");
        setIsUploading(false);
      };
      
      xhr.ontimeout = function() {
        console.error('XHR request timed out');
        setError("Request timed out. The server is taking too long to respond. Please try again later.");
        setIsUploading(false);
      };
      
      xhr.send(formData);
    } catch (err) {
      console.error("Submission error:", err);
      setError("Something went wrong. Please try again.");
      setIsUploading(false);
    }
  }

  const handleDownload = () => {
    if (improvedResumePdf) {
      const link = document.createElement("a")
      link.href = improvedResumePdf
      link.download = "improved-resume.pdf"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <div className="container mx-auto px-4 py-16 md:py-24">
      {/* Hero Section */}
      <header className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
          Turn Your Good Resume Into a Great One — Instantly.
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 mb-10">
          First impressions matter — we make sure yours is unforgettable.
        </p>

        {/* Trust Bullets */}
        <section aria-labelledby="benefits" className="mb-12">
          <h2 id="benefits" className="sr-only">Benefits</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12 max-w-2xl mx-auto text-left">
            {[
              "Instant resume makeover",
              "Clear, modern formatting that recruiters love",
              "Highlight your strengths automatically",
              "ATS-friendly (passes resume scanning software)",
              "100% secure — your info stays private",
            ].map((bullet, index) => (
              <div key={index} className="flex items-start space-x-2">
                <Check className="h-5 w-5 text-emerald-500 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <span className="text-gray-700">{bullet}</span>
              </div>
            ))}
          </div>
        </section>

        {/* CTA Button */}
        <section aria-labelledby="cta-section" className="mb-12">
          <h2 id="cta-section" className="sr-only">Get Started</h2>
          {!improvedResumePdf ? (
            <Button
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-full px-8 py-6 text-lg font-medium shadow-lg hover:shadow-xl transition-all"
              onClick={() => setIsModalOpen(true)}
              aria-label="Upload and improve your resume"
            >
              Make My Resume Shine
            </Button>
          ) : (
            <div className="space-y-4">
              <PdfViewer pdfUrl={improvedResumePdf} />
              <Button
                size="lg"
                className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-full px-8 py-6 text-lg font-medium shadow-lg hover:shadow-xl transition-all"
                onClick={handleDownload}
                aria-label="Download your improved resume"
              >
                <Download className="mr-2 h-5 w-5" aria-hidden="true" />
                Download Improved Resume
              </Button>
            </div>
          )}
        </section>
      </header>

      {/* Upload Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Upload your current resume</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center cursor-pointer hover:bg-gray-50 transition-colors">
              <input 
                type="file" 
                id="resume-upload" 
                accept=".pdf" 
                onChange={handleFileChange} 
                className="hidden" 
                aria-label="Upload resume PDF"
              />
              <label htmlFor="resume-upload" className="cursor-pointer">
                <Upload className="h-10 w-10 text-gray-400 mx-auto mb-4" aria-hidden="true" />
                <p className="text-sm text-gray-500 mb-1">{file ? file.name : "Click to upload or drag and drop"}</p>
                <p className="text-xs text-gray-400">PDF files only (max 10MB)</p>
              </label>
            </div>

            {error && <p className="text-red-500 text-sm" role="alert">{error}</p>}

            <div className="flex justify-end">
              <Button 
                type="submit" 
                disabled={!file || isUploading} 
                className="bg-emerald-600 hover:bg-emerald-700"
                aria-label={isUploading ? "Uploading resume..." : "Improve my resume"}
                aria-busy={isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                    Uploading...
                  </>
                ) : (
                  "Improve My Resume"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
