"use client"

import { Button } from "@/components/ui/button"
import { FolderOpen, CheckCircle, Clock, Download } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/ui/sidebar"
import { isAuthenticated, signOut } from "@/lib/utils"

export default function HistoryPage() {
  const [isFormSubmitted, setIsFormSubmitted] = useState(false)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    let active = true
    isAuthenticated().then((ok) => {
      if (!active) return
      if (!ok) {
        router.push("/")
      } else {
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [router])

  const handleLogout = async () => {
    await signOut()
    router.push("/")
  }

  const handleFormSubmit = () => {
    setIsFormSubmitted(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="size-12 animate-spin rounded-full border-[3px] border-border border-t-brand"></div>
      </div>
    )
  }

  return (
    <div className="ambient-glow relative min-h-screen bg-background">
      {/* Sidebar */}
      <Sidebar onLogout={handleLogout} />

      <div className="container-page py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <a
              href="https://drive.google.com"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-2xl border border-border bg-card p-4 shadow-sm transition-shadow duration-200 hover:shadow-md"
            >
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/1/12/Google_Drive_icon_%282020%29.svg"
                alt="Google Drive"
                className="h-14 w-14"
              />
            </a>
          </div>

          <h1 className="mb-3 text-2xl font-bold tracking-tight md:text-3xl">
            Give us your Gmail address
          </h1>

          <p className="mx-auto max-w-xl text-lg text-muted-foreground">
            We&apos;ll share your generated documents on{' '}
            <a
              href="https://drive.google.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 font-medium text-brand underline hover:no-underline"
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
        <div className="mx-auto mb-12 max-w-4xl">
          <h2 className="mb-8 text-center text-2xl font-bold tracking-tight">
            How it works
          </h2>

          <div className="grid gap-6 md:grid-cols-3">
            <div className="surface p-6 text-center">
              <div className="mx-auto mb-4 w-fit rounded-full bg-brand/10 p-3">
                <FolderOpen className="h-7 w-7 text-brand" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Complete document access
              </h3>
              <p className="text-sm text-muted-foreground">
                Access all your generated resumes, cover letters, and application materials in one organized location.
              </p>
            </div>

            <div className="surface p-6 text-center">
              <div className="mx-auto mb-4 w-fit rounded-full bg-[var(--accent2)]/10 p-3">
                <Download className="h-7 w-7 text-[var(--accent2)]" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Instant local sync
              </h3>
              <p className="mb-3 text-sm text-muted-foreground">
                Install Google Drive on your computer and files sync instantly to your laptop for offline access.
              </p>
              <a
                href="https://support.google.com/a/users/answer/13022292?hl=en#drive_desktop_install"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs font-medium text-[var(--accent2)] underline hover:no-underline"
              >
                Install for Mac/Windows
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>

            <div className="surface p-6 text-center">
              <div className="mx-auto mb-4 w-fit rounded-full bg-[var(--success)]/10 p-3">
                <Clock className="h-7 w-7 text-[var(--success)]" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">
                Always available
              </h3>
              <p className="text-sm text-muted-foreground">
                Your documents are automatically synced and available 24/7 through Google Drive and your local machine.
              </p>
            </div>
          </div>
        </div>

        {/* Main Form Section */}
        <div className="mx-auto mb-12 max-w-2xl">
          {!isFormSubmitted ? (
            <div className="surface p-4 md:p-8">
              {/* Google Form */}
              <div className="flex justify-center">
                <div className="w-full overflow-hidden rounded-xl bg-white">
                  <iframe
                    src="https://docs.google.com/forms/d/e/1FAIpQLScLVM0Rilffz_fxX_Lbuh0PDo0OdyTdatHgiDn0U-q9Es0Dlg/viewform?embedded=true"
                    className="h-[700px] w-full"
                    frameBorder={0}
                    marginHeight={0}
                    marginWidth={0}
                    title="Share your Gmail address"
                    onLoad={() => {
                      const iframe = document.querySelector('iframe');
                      if (iframe) {
                        iframe.addEventListener('load', () => {
                          setTimeout(() => {
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
            <div className="surface p-8 text-center">
              <div className="mb-4 flex justify-center">
                <div className="rounded-full bg-[var(--success)]/10 p-3">
                  <CheckCircle className="h-8 w-8 text-[var(--success)]" />
                </div>
              </div>

              <h2 className="mb-3 text-xl font-bold">
                Thank you!
              </h2>

              <p className="mb-6 text-muted-foreground">
                We&apos;ve received your Gmail address. Our team will set up your personal folder and share it with you within 24 hours.
              </p>

              <div className="rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/10 p-4 text-left">
                <h3 className="mb-2 text-sm font-semibold text-[var(--success)]">
                  What to expect:
                </h3>
                <ul className="space-y-1 text-xs text-muted-foreground">
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