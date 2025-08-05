"use client"

import { Button } from "@/components/ui/button"
import { ArrowLeft, History, FolderOpen, Share2, Mail, CheckCircle, Clock, Download } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/ui/sidebar"
import { isAuthenticated, removeAccessToken, removeUserData } from "@/lib/utils"

export default function HistoryPage() {
  const [isFormSubmitted, setIsFormSubmitted] = useState(false)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push("/")
    } else {
      setLoading(false)
    }
  }, [router])

  const handleLogout = () => {
    removeAccessToken()
    removeUserData()
    router.push("/")
  }

  const handleFormSubmit = () => {
    setIsFormSubmitted(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-blue-50/30 dark:from-gray-950 dark:to-blue-950/30">
      {/* Sidebar */}
      <Sidebar onLogout={handleLogout} />

      {/* Decorative background elements */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/4 top-1/4 h-48 w-48 md:h-64 md:w-64 rounded-full bg-blue-200/10 blur-3xl dark:bg-blue-900/10"></div>
        <div className="absolute right-1/4 bottom-1/3 h-64 w-64 md:h-96 md:w-96 rounded-full bg-purple-200/10 blur-3xl dark:bg-purple-900/10"></div>
        <div className="absolute left-1/3 bottom-1/4 h-32 w-32 md:h-48 md:w-48 rounded-full bg-green-200/10 blur-3xl dark:bg-green-900/10"></div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <a 
              href="https://drive.google.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="p-3 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow duration-200 cursor-pointer"
            >
              <img 
                src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg" 
                alt="Google Drive" 
                className="h-16 w-16"
              />
            </a>
          </div>
          
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-3">
            Give us your Gmail address
          </h1>
          
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-xl mx-auto">
            We'll share your generated documents on{' '}
            <a 
              href="https://drive.google.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline font-medium inline-flex items-center gap-1"
            >
              Google Drive
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
            {' '}with you.
          </p>
        </div>

        {/* Benefits Section */}
        <div className="max-w-4xl mx-auto mb-12">
          <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-8">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 text-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full w-fit mx-auto mb-4">
                <FolderOpen className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Complete Document Access
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Access all your generated resumes, cover letters, and application materials in one organized location.
              </p>
            </div>

            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 text-center">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full w-fit mx-auto mb-4">
                <Download className="h-8 w-8 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Instant Local Sync
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">
                Install Google Drive on your computer and files sync instantly to your laptop for offline access.
              </p>
              <a 
                href="https://support.google.com/a/users/answer/13022292?hl=en#drive_desktop_install" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-purple-600 hover:text-purple-800 text-xs font-medium inline-flex items-center gap-1 underline"
              >
                Install for Mac/Windows
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>

            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-6 text-center">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full w-fit mx-auto mb-4">
                <Clock className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Always Available
              </h3>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Your documents are automatically synced and available 24/7 through Google Drive and your local machine.
              </p>
            </div>
          </div>
        </div>

        {/* Main Form Section */}
        <div className="max-w-2xl mx-auto mb-12">
          {!isFormSubmitted ? (
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-8">


              {/* Google Form */}
              <div className="flex justify-center">
                <div className="w-full">
                  <iframe 
                    src="https://docs.google.com/forms/d/e/1FAIpQLScLVM0Rilffz_fxX_Lbuh0PDo0OdyTdatHgiDn0U-q9Es0Dlg/viewform?embedded=true" 
                    width={640}
                    height={700}
                    frameBorder={0}
                    marginHeight={0}
                    marginWidth={0}
                    onLoad={() => {
                      // Listen for form submission
                      const iframe = document.querySelector('iframe');
                      if (iframe) {
                        iframe.addEventListener('load', () => {
                          // This is a basic approach - in a real implementation you might want to use Google Forms API
                          setTimeout(() => {
                            // Check if form was submitted (this is a simplified approach)
                            if (window.location.href.includes('formResponse')) {
                              handleFormSubmit()
                            }
                          }, 1000)
                        })
                      }
                    }}
                  >
                    Loading…
                  </iframe>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 dark:border-gray-700/50 p-8 text-center">
              <div className="flex justify-center mb-4">
                <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
                  <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
                </div>
              </div>
              
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                Thank You!
              </h2>
              
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                We've received your Gmail address. Our team will set up your personal folder and share it with you within 24 hours.
              </p>

              <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4 border border-green-200 dark:border-green-800">
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2 text-sm">
                  What to expect:
                </h3>
                <ul className="text-xs text-green-800 dark:text-green-200 space-y-1">
                  <li>• Email notification within 24 hours</li>
                  <li>• Access to your Google Drive folder</li>
                  <li>• All your documents organized by company</li>
                  <li>• Automatic updates for future documents</li>
                </ul>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  )
} 