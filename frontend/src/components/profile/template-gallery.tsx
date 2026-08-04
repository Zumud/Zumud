"use client"

/**
 * The templates a user can pick between, and the .tex uploader that adds to them.
 *
 * Uploading is not a request that finishes: converting a document into a template
 * takes a model several attempts and a real compile each time, so the server answers
 * immediately with the template in a pending state and does the work afterwards. That
 * makes this component the thing that has to notice it finished — hence the polling
 * while anything is pending, and why a pending or failed template is shown but cannot
 * be chosen.
 */

import { type ChangeEvent, type DragEvent, useCallback, useEffect, useRef, useState } from "react"
import { AlertTriangle, Check, Loader2, Trash2, Upload } from "lucide-react"
import Image from "next/image"

import { templates, type ResumeTemplate } from "@/lib/api"

// Mirrors MAX_UPLOAD_BYTES in backend/core/template_service.py. Checked here only to
// answer instantly; the server is the authority and repeats every one of its checks.
const MAX_UPLOAD_BYTES = 256 * 1024

// Conversion takes tens of seconds, so this is often enough to feel live without
// making a request per second for something that cannot be hurried.
const POLL_MS = 3000

type Props = {
  onError: (error: unknown, fallback: string) => void
  onSuccess: (message: string) => void
}

function statusLine(template: ResumeTemplate) {
  if (template.status === "pending") return "Converting your LaTeX into a template..."
  if (template.status === "failed") return template.error || "That file could not be converted."
  return template.description
}

export default function TemplateGallery({ onError, onSuccess }: Props) {
  const [gallery, setGallery] = useState<ResumeTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [confirmingRemoval, setConfirmingRemoval] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const converting = gallery.some((template) => template.status === "pending")

  const refresh = useCallback(async () => {
    try {
      setGallery(await templates.list())
    } catch (err) {
      console.error("Failed to load templates:", err)
      onError(err, "Failed to load your templates. Please try again later.")
    }
  }, [onError])

  useEffect(() => {
    const timeoutId = window.setTimeout(async () => {
      await refresh()
      setLoading(false)
    }, 0)
    return () => window.clearTimeout(timeoutId)
  }, [refresh])

  useEffect(() => {
    if (!converting) return
    const intervalId = window.setInterval(() => void refresh(), POLL_MS)
    return () => window.clearInterval(intervalId)
  }, [converting, refresh])

  const handleSelect = async (slug: string) => {
    const previous = gallery
    setBusy(true)
    // Moved before the request lands so the click feels immediate; the response is
    // the authority, and a failure puts the old choice back.
    setGallery(gallery.map((template) => ({ ...template, selected: template.slug === slug })))

    try {
      setGallery(await templates.select(slug))
      onSuccess("Template updated. Your next resume will use it.")
    } catch (err) {
      setGallery(previous)
      onError(err, "Failed to change your template.")
    } finally {
      setBusy(false)
    }
  }

  const handleUpload = async (file: File) => {
    if (!file.name.toLowerCase().endsWith(".tex")) {
      onError(null, "Upload the .tex source of your resume.")
      return
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      onError(
        null,
        `That file is larger than ${MAX_UPLOAD_BYTES / 1024}KB. Upload just the .tex source, without its images or fonts.`
      )
      return
    }

    setBusy(true)
    try {
      setGallery(await templates.upload(file))
      onSuccess("Converting your template. This takes a minute — you can stay on this page.")
    } catch (err) {
      onError(err, "Failed to upload that file.")
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (slug: string) => {
    setBusy(true)
    try {
      setGallery(await templates.remove(slug))
      setConfirmingRemoval(null)
      onSuccess("Template removed.")
    } catch (err) {
      onError(err, "Failed to remove that template.")
    } finally {
      setBusy(false)
    }
  }

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    // Cleared so choosing the same file twice — after a failed conversion, say — still
    // counts as a change.
    event.target.value = ""
    if (file) void handleUpload(file)
  }

  const handleDrop = (event: DragEvent<HTMLLIElement>) => {
    event.preventDefault()
    setDragging(false)
    const file = event.dataTransfer.files?.[0]
    if (file) void handleUpload(file)
  }

  return (
    <section className="surface mb-6 p-6">
      <h2 className="text-xl font-semibold">Resume template</h2>
      <p className="mt-1 text-sm text-muted-foreground">
        The design every resume you generate is built with. Pick one of ours, or upload your
        own LaTeX and we will turn it into a template. Changing it affects your next resume,
        not the ones you have already made.
      </p>

      {loading ? (
        <div className="mt-5 flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading templates...
        </div>
      ) : (
        <ul className="mt-5 grid list-none gap-4 p-0 sm:grid-cols-2 lg:grid-cols-3">
          {gallery.map((template) => {
            const own = template.slug.startsWith("user:")
            const ready = template.status === "ready"

            return (
              <li
                key={template.slug}
                className={`flex flex-col overflow-hidden rounded-xl border transition-colors ${
                  template.selected ? "border-brand ring-1 ring-brand" : "border-border"
                }`}
              >
                <button
                  type="button"
                  onClick={() => handleSelect(template.slug)}
                  disabled={busy || template.selected || !ready}
                  aria-pressed={template.selected}
                  // Named for what the click does: the visible text is a collage of
                  // thumbnail caption, title and status that reads as none of it.
                  aria-label={`Use the ${template.name} template`}
                  className="group flex flex-1 cursor-pointer flex-col text-left transition-colors hover:bg-muted/30 disabled:cursor-default disabled:hover:bg-transparent"
                >
                  <span className="relative block aspect-[3/4] w-full overflow-hidden border-b border-border bg-muted/30">
                    {template.preview_url ? (
                      <Image
                        src={template.preview_url}
                        alt={`A resume built with the ${template.name} template`}
                        fill
                        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                        className="object-cover object-top"
                      />
                    ) : (
                      <span className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center text-xs text-muted-foreground">
                        {template.status === "pending" ? (
                          <Loader2 className="h-6 w-6 animate-spin text-brand" />
                        ) : template.status === "failed" ? (
                          <AlertTriangle className="h-6 w-6 text-destructive" />
                        ) : null}
                        Your own template
                      </span>
                    )}
                    {template.selected && (
                      <span className="absolute right-2 top-2 flex items-center gap-1 rounded-full bg-brand px-2 py-1 text-xs font-medium text-brand-foreground">
                        <Check className="h-3 w-3" />
                        In use
                      </span>
                    )}
                  </span>
                  <span className="flex flex-1 flex-col gap-1 p-3">
                    <span className="text-sm font-medium">{template.name}</span>
                    <span
                      className={`text-xs ${
                        template.status === "failed" ? "text-destructive" : "text-muted-foreground"
                      }`}
                    >
                      {statusLine(template)}
                    </span>
                  </span>
                </button>

                {own && (
                  <div className="border-t border-border px-3 py-2 text-right">
                    {confirmingRemoval === template.slug ? (
                      <span className="flex items-center justify-end gap-3 text-xs">
                        <button
                          type="button"
                          onClick={() => setConfirmingRemoval(null)}
                          className="cursor-pointer text-muted-foreground hover:underline"
                        >
                          Keep
                        </button>
                        <button
                          type="button"
                          onClick={() => void handleRemove(template.slug)}
                          disabled={busy}
                          className="cursor-pointer font-medium text-destructive hover:underline"
                        >
                          Remove for good
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setConfirmingRemoval(template.slug)}
                        disabled={busy}
                        className="inline-flex cursor-pointer items-center gap-1 text-xs text-muted-foreground hover:text-destructive"
                        aria-label={`Remove ${template.name}`}
                      >
                        <Trash2 className="h-3 w-3" />
                        Remove
                      </button>
                    )}
                  </div>
                )}
              </li>
            )
          })}

          <li
            onDragOver={(event) => {
              event.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            className={`flex flex-col items-center justify-center gap-2 rounded-xl border border-dashed p-6 text-center transition-colors ${
              dragging ? "border-brand bg-brand/5" : "border-border"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".tex"
              className="hidden"
              onChange={handleFileChange}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={busy || converting}
              className="flex h-12 w-12 cursor-pointer items-center justify-center rounded-full bg-brand/10 text-brand transition-colors hover:bg-brand/20 disabled:cursor-default disabled:opacity-50"
              aria-label="Upload your LaTeX resume"
            >
              {busy ? <Loader2 className="h-5 w-5 animate-spin" /> : <Upload className="h-5 w-5" />}
            </button>
            <span className="text-sm font-medium">Upload your LaTeX</span>
            <span className="text-xs text-muted-foreground">
              {converting
                ? "One at a time — your last upload is still converting."
                : `Drop a .tex file here, up to ${MAX_UPLOAD_BYTES / 1024}KB.`}
            </span>
          </li>
        </ul>
      )}
    </section>
  )
}
