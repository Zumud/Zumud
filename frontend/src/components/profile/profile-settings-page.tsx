"use client"

import { type ChangeEvent, type KeyboardEvent, type MouseEvent, useEffect, useRef, useState } from "react"
import {
  CheckCircle,
  Edit3,
  Loader2,
  LogIn,
  Plus,
  Power,
  PowerOff,
  Save,
  Trash2,
  Upload,
  X,
} from "lucide-react"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { account, aiRules, resume, type CurrentUser, type UserAIRule } from "@/lib/api"
import { errorMessage, signOut } from "@/lib/utils"
import TemplateGallery from "./template-gallery"

const AI_RULE_INSTRUCTION_MAX = 500

type RuleFormState = {
  title: string
  instruction: string
}

const emptyRuleForm: RuleFormState = {
  title: "",
  instruction: "",
}

function isAuthMessage(message: string | null) {
  return Boolean(
    message &&
      (message.includes("session has expired") ||
        message.includes("login") ||
        message.includes("token") ||
        message.includes("unauthorized") ||
        message.includes("authentication"))
  )
}

function sortRulesByUpdatedDate(rules: UserAIRule[]) {
  return [...rules].sort((a, b) => {
    const updatedDiff = new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
    return updatedDiff || a.id - b.id
  })
}

function ruleTitle(rule: UserAIRule) {
  return rule.title || "Untitled rule"
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

export default function ProfileSettingsPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isAuthError, setIsAuthError] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [accountData, setAccountData] = useState<CurrentUser | null>(null)
  const [accountLoading, setAccountLoading] = useState(false)
  const [resumeData, setResumeData] = useState<string>("")

  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [rules, setRules] = useState<UserAIRule[]>([])
  const [rulesLoading, setRulesLoading] = useState(false)
  const [ruleForm, setRuleForm] = useState<RuleFormState>(emptyRuleForm)
  const [editingRuleId, setEditingRuleId] = useState<number | null>(null)
  const [savingRuleId, setSavingRuleId] = useState<number | null>(null)
  const [selectedRule, setSelectedRule] = useState<UserAIRule | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<UserAIRule | null>(null)
  const [isDeletingRule, setIsDeletingRule] = useState(false)

  const redirectToLogin = async () => {
    await signOut()
    router.push("/")
  }

  const showError = (err: unknown, fallback: string) => {
    const message = errorMessage(err)
    if (isAuthMessage(message)) {
      setError("Your session has expired. Please log in again to continue.")
      setIsAuthError(true)
      return
    }

    setError(message || fallback)
    setIsAuthError(false)
  }

  const fetchResumeData = async () => {
    try {
      const data = await resume.getResume()
      if (data && data.resume_content) {
        setResumeData(data.resume_content)
      }
      setIsAuthError(false)
    } catch (err) {
      console.error("Failed to load resume:", err)
      showError(err, "Failed to load your current resume. Please try again later.")
    }
  }

  const fetchAccountData = async () => {
    setAccountLoading(true)
    try {
      const data = await account.me()
      setAccountData(data)
      setIsAuthError(false)
    } catch (err) {
      console.error("Failed to load account:", err)
      showError(err, "Failed to load your account details. Please try again later.")
    } finally {
      setAccountLoading(false)
    }
  }

  const fetchAIRules = async () => {
    setRulesLoading(true)
    try {
      const savedRules = await aiRules.list()
      setRules(sortRulesByUpdatedDate(savedRules))
      setIsAuthError(false)
    } catch (err) {
      console.error("Failed to load AI rules:", err)
      showError(err, "Failed to load your AI rules. Please try again later.")
    } finally {
      setRulesLoading(false)
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void fetchAccountData()
      void fetchResumeData()
      void fetchAIRules()
    }, 0)
    return () => window.clearTimeout(timeoutId)
    // eslint-disable-next-line react-hooks/exhaustive-deps -- initial profile data load
  }, [])

  const handleUpdateResume = async () => {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    setIsAuthError(false)

    try {
      await resume.updateResume(resumeData)
      setSuccess("Resume text updated successfully.")
    } catch (err) {
      showError(err, "Failed to update resume text.")
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploadStatus("idle")
    setError(null)
    setIsAuthError(false)

    if (file.type !== "application/pdf") {
      setError("Please upload a PDF file.")
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("File size exceeds the 5MB limit.")
      return
    }

    setResumeFile(file)
  }

  const handleUploadResume = async () => {
    if (!resumeFile) {
      setError("Please select a PDF file first.")
      return
    }

    setUploadStatus("uploading")
    setError(null)
    setSuccess(null)
    setIsAuthError(false)

    try {
      await resume.uploadResumePdf(resumeFile)
      setUploadStatus("success")
      setSuccess("Resume uploaded successfully.")
      await fetchResumeData()

      setTimeout(() => {
        setResumeFile(null)
        setUploadStatus("idle")
        if (fileInputRef.current) {
          fileInputRef.current.value = ""
        }
      }, 3000)
    } catch (err) {
      setUploadStatus("error")
      showError(err, "Failed to upload resume.")
    }
  }

  const resetRuleForm = () => {
    setRuleForm(emptyRuleForm)
    setEditingRuleId(null)
  }

  const startEditingRule = (rule: UserAIRule) => {
    setRuleForm({
      title: rule.title || "",
      instruction: rule.instruction,
    })
    setEditingRuleId(rule.id)
    setSelectedRule(null)
  }

  const syncRule = (updatedRule: UserAIRule) => {
    setRules((current) => sortRulesByUpdatedDate(current.map((rule) => (rule.id === updatedRule.id ? updatedRule : rule))))
    setSelectedRule((current) => (current?.id === updatedRule.id ? updatedRule : current))
  }

  const handleSaveRule = async () => {
    const instruction = ruleForm.instruction.trim()
    const title = ruleForm.title.trim()

    setError(null)
    setSuccess(null)
    setIsAuthError(false)

    if (!instruction) {
      setError("AI rule instruction cannot be empty.")
      return
    }

    if (instruction.length > AI_RULE_INSTRUCTION_MAX) {
      setError(`AI rule instruction must be ${AI_RULE_INSTRUCTION_MAX} characters or fewer.`)
      return
    }

    setSavingRuleId(editingRuleId ?? 0)
    try {
      if (editingRuleId) {
        const updatedRule = await aiRules.update(editingRuleId, {
          title: title || null,
          instruction,
        })
        syncRule(updatedRule)
        setSuccess("AI rule updated.")
      } else {
        const createdRule = await aiRules.create({
          title: title || null,
          instruction,
        })
        setRules((current) => sortRulesByUpdatedDate([createdRule, ...current]))
        setSuccess("AI rule added.")
      }
      resetRuleForm()
    } catch (err) {
      showError(err, "Failed to save AI rule.")
    } finally {
      setSavingRuleId(null)
    }
  }

  const handleToggleRule = async (rule: UserAIRule) => {
    setSavingRuleId(rule.id)
    setError(null)
    setSuccess(null)
    try {
      const updatedRule = await aiRules.update(rule.id, { is_enabled: !rule.is_enabled })
      syncRule(updatedRule)
    } catch (err) {
      showError(err, "Failed to update AI rule.")
    } finally {
      setSavingRuleId(null)
    }
  }

  const handleConfirmDeleteRule = async () => {
    if (!deleteTarget) return

    setIsDeletingRule(true)
    setError(null)
    setSuccess(null)
    try {
      await aiRules.delete(deleteTarget.id)
      setRules((current) => current.filter((rule) => rule.id !== deleteTarget.id))
      if (editingRuleId === deleteTarget.id) {
        resetRuleForm()
      }
      if (selectedRule?.id === deleteTarget.id) {
        setSelectedRule(null)
      }
      setSuccess("AI rule deleted.")
      setDeleteTarget(null)
    } catch (err) {
      showError(err, "Failed to delete AI rule.")
    } finally {
      setIsDeletingRule(false)
    }
  }

  const stopRowAction = (event: MouseEvent<HTMLButtonElement>, action: () => void) => {
    event.stopPropagation()
    action()
  }

  const handleRuleRowKeyDown = (event: KeyboardEvent<HTMLDivElement>, rule: UserAIRule) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault()
      setSelectedRule(rule)
    }
  }

  const remainingInstructionChars = AI_RULE_INSTRUCTION_MAX - ruleForm.instruction.length

  return (
    <div className="min-h-screen bg-background">
      <div className="container-page max-w-3xl py-8 md:py-12">
        <div className="mb-8">
          <h1 className="text-2xl font-bold tracking-tight">Profile settings</h1>
        </div>

        {error && (
          <div className="mb-6 rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive" role="alert">
            <div className="flex items-start justify-between gap-4">
              <span className="block sm:inline">{error}</span>
              {isAuthError && (
                <Button variant="outline" size="sm" onClick={redirectToLogin} className="shrink-0">
                  <LogIn className="mr-2 h-4 w-4" />
                  Log in
                </Button>
              )}
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 rounded-xl border border-[var(--success)]/30 bg-[var(--success)]/10 px-4 py-3 text-sm text-[var(--success)]" role="alert">
            <span className="block sm:inline">{success}</span>
          </div>
        )}

        <section className="surface mb-6 p-6">
          <h2 className="text-xl font-semibold">Account</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Your sign-in details are shown here for reference.
          </p>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-muted-foreground">Username</span>
              <input
                value={accountLoading ? "Loading..." : accountData?.username || ""}
                readOnly
                tabIndex={-1}
                className="field cursor-default bg-muted/30 focus-visible:border-input focus-visible:ring-0"
                aria-readonly="true"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-muted-foreground">Email</span>
              <input
                value={accountLoading ? "Loading..." : accountData?.email || ""}
                readOnly
                tabIndex={-1}
                className="field cursor-default bg-muted/30 focus-visible:border-input focus-visible:ring-0"
                aria-readonly="true"
              />
            </label>
          </div>
        </section>

        <div className="surface mb-6 p-6">
          <h2 className="text-xl font-semibold">Manage your resume</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Edit your resume text directly or upload a new PDF resume.
          </p>

          <Tabs defaultValue="edit" className="mt-5">
            <TabsList className="mb-4 w-full">
              <TabsTrigger value="edit" className="flex-1">Edit resume text</TabsTrigger>
              <TabsTrigger value="upload" className="flex-1">Upload PDF resume</TabsTrigger>
            </TabsList>

            <TabsContent value="edit" className="space-y-4">
              <textarea
                value={resumeData}
                onChange={(e) => setResumeData(e.target.value)}
                className="field h-96 resize-none"
                placeholder="Your resume content here..."
              />

              <div className="flex justify-end">
                <Button onClick={handleUpdateResume} variant="brand" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save resume
                    </>
                  )}
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="upload" className="space-y-4">
              <div className="rounded-xl border border-border">
                <div className="p-4">
                  {uploadStatus === "success" ? (
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-8 w-8 shrink-0 text-[var(--success)]" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">{resumeFile?.name}</p>
                        <p className="text-sm text-[var(--success)]">Resume uploaded successfully.</p>
                      </div>
                    </div>
                  ) : uploadStatus === "uploading" ? (
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-8 w-8 shrink-0 animate-spin text-brand" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">Processing resume...</p>
                        <p className="text-sm text-muted-foreground">This may take a moment</p>
                      </div>
                    </div>
                  ) : (
                    <div className="py-8 text-center">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="application/pdf"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                      <button
                        type="button"
                        className="mx-auto mb-3 flex h-16 w-16 cursor-pointer items-center justify-center rounded-full bg-brand/10 text-brand transition-colors hover:bg-brand/20"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <Upload className="h-8 w-8" />
                      </button>
                      <p className="text-sm">
                        <button
                          type="button"
                          className="cursor-pointer font-medium text-brand hover:underline"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Click to upload
                        </button>{" "}
                        or drag and drop
                      </p>
                      <p className="mt-1 text-xs text-muted-foreground">PDF up to 5MB</p>

                      {resumeFile && (
                        <div className="mt-3">
                          <p className="text-sm font-medium">{resumeFile.name}</p>
                          <Button type="button" onClick={handleUploadResume} variant="brand" className="mt-2" size="sm">
                            Upload resume
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div className="text-sm text-muted-foreground">
                <p>When you upload a new resume, we&apos;ll automatically extract the text content for you.</p>
                <p>This will replace your current resume text.</p>
              </div>
            </TabsContent>
          </Tabs>
        </div>

        <TemplateGallery
          onError={(err, fallback) => {
            setSuccess(null)
            showError(err, fallback)
          }}
          onSuccess={(message) => {
            setError(null)
            setIsAuthError(false)
            setSuccess(message)
          }}
        />

        <section className="surface mb-6 p-6">
          <div>
            <h2 className="text-xl font-semibold">AI Rules</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              These rules will be applied automatically whenever AI generates or edits content for you. Enabled rules take precedence over general templates and default AI preferences.
            </p>
          </div>

          <div className="mt-5 space-y-4 rounded-xl border border-border p-4">
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-muted-foreground">Optional title</span>
              <input
                value={ruleForm.title}
                onChange={(event) => setRuleForm((current) => ({ ...current, title: event.target.value }))}
                className="field"
                maxLength={120}
                placeholder="Resume length"
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs font-medium text-muted-foreground">Instruction</span>
              <textarea
                value={ruleForm.instruction}
                onChange={(event) => setRuleForm((current) => ({ ...current, instruction: event.target.value }))}
                className="field min-h-28 resize-y"
                maxLength={AI_RULE_INSTRUCTION_MAX}
                placeholder="Keep my resume under two pages."
              />
            </label>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className={`text-xs ${remainingInstructionChars < 0 ? "text-destructive" : "text-muted-foreground"}`}>
                {remainingInstructionChars} characters remaining
              </p>
              <div className="flex justify-end gap-2">
                {editingRuleId && (
                  <Button type="button" variant="outline" onClick={resetRuleForm}>
                    <X className="mr-2 h-4 w-4" />
                    Cancel
                  </Button>
                )}
                <Button type="button" variant="brand" onClick={handleSaveRule} disabled={savingRuleId !== null}>
                  {savingRuleId === (editingRuleId ?? 0) ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : editingRuleId ? (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save rule
                    </>
                  ) : (
                    <>
                      <Plus className="mr-2 h-4 w-4" />
                      Add rule
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>

          <div className="mt-5">
            {rulesLoading ? (
              <div className="flex items-center gap-2 rounded-xl border border-border p-4 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading AI rules...
              </div>
            ) : rules.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border bg-muted/40 p-6">
                <p className="text-sm font-medium">No AI rules yet</p>
                <div className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <p>Keep my resume under two pages.</p>
                  <p>Always write application documents in English.</p>
                  <p>Use concise and professional language.</p>
                </div>
              </div>
            ) : (
              <div className="divide-y divide-border rounded-xl border border-border">
                {rules.map((rule) => (
                  <div
                    key={rule.id}
                    role="button"
                    tabIndex={0}
                    aria-label={`View AI rule details for ${ruleTitle(rule)}`}
                    onClick={() => setSelectedRule(rule)}
                    onKeyDown={(event) => handleRuleRowKeyDown(event, rule)}
                    className="flex min-h-12 cursor-pointer items-center gap-3 px-3 py-2 outline-none transition-colors hover:bg-muted/50 focus-visible:bg-muted/50 focus-visible:ring-[3px] focus-visible:ring-ring/35"
                  >
                    <span className={`min-w-0 flex-1 truncate text-sm font-medium ${rule.is_enabled ? "text-foreground" : "text-muted-foreground line-through opacity-70"}`}>
                      {ruleTitle(rule)}
                    </span>
                    <div className="flex shrink-0 items-center gap-1">
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        title={rule.is_enabled ? "Disable rule" : "Enable rule"}
                        aria-label={rule.is_enabled ? `Disable ${ruleTitle(rule)}` : `Enable ${ruleTitle(rule)}`}
                        disabled={savingRuleId !== null}
                        onClick={(event) => stopRowAction(event, () => handleToggleRule(rule))}
                      >
                        {savingRuleId === rule.id ? <Loader2 className="h-4 w-4 animate-spin" /> : rule.is_enabled ? <Power className="h-4 w-4" /> : <PowerOff className="h-4 w-4" />}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        title="Edit rule"
                        aria-label={`Edit ${ruleTitle(rule)}`}
                        disabled={savingRuleId !== null}
                        onClick={(event) => stopRowAction(event, () => startEditingRule(rule))}
                      >
                        <Edit3 className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        variant="destructive"
                        size="icon"
                        title="Delete rule"
                        aria-label={`Delete ${ruleTitle(rule)}`}
                        disabled={savingRuleId !== null}
                        onClick={(event) => stopRowAction(event, () => setDeleteTarget(rule))}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

      </div>

      <Dialog open={selectedRule !== null} onOpenChange={(open) => !open && setSelectedRule(null)}>
        <DialogContent className="max-h-[85vh] overflow-hidden p-0 sm:max-w-xl">
          {selectedRule && (
            <>
              <DialogHeader className="border-b border-border bg-muted/30 px-6 py-5 pr-12">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${selectedRule.is_enabled ? "bg-[var(--success)]/10 text-[var(--success)]" : "bg-muted text-muted-foreground"}`}>
                    {selectedRule.is_enabled ? "Enabled" : "Disabled"}
                  </span>
                </div>
                <DialogTitle className={`mt-3 text-xl leading-tight ${selectedRule.is_enabled ? "" : "text-muted-foreground line-through"}`}>
                  {ruleTitle(selectedRule)}
                </DialogTitle>
              </DialogHeader>

              <div className="max-h-[calc(85vh-9rem)] space-y-5 overflow-y-auto px-6 py-5">
                <div className="rounded-xl border border-border bg-background p-4 shadow-xs">
                  <p className="text-xs font-semibold uppercase text-muted-foreground">Instruction</p>
                  <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-6">{selectedRule.instruction}</p>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-xl border border-border bg-muted/25 p-3">
                    <p className="text-xs font-semibold uppercase text-muted-foreground">Created</p>
                    <p className="mt-1 break-words text-sm">{formatDate(selectedRule.created_at)}</p>
                  </div>
                  <div className="rounded-xl border border-border bg-muted/25 p-3">
                    <p className="text-xs font-semibold uppercase text-muted-foreground">Last updated</p>
                    <p className="mt-1 break-words text-sm">{formatDate(selectedRule.updated_at)}</p>
                  </div>
                </div>
              </div>

              <div className="flex flex-col-reverse gap-2 border-t border-border bg-muted/20 px-6 py-4 sm:flex-row sm:justify-between">
                <Button type="button" variant="outline" onClick={() => setSelectedRule(null)}>
                  Close
                </Button>
                <div className="flex flex-col gap-2 sm:flex-row">
                  <Button type="button" variant="outline" onClick={() => void handleToggleRule(selectedRule)} disabled={savingRuleId !== null}>
                    {selectedRule.is_enabled ? <Power className="mr-2 h-4 w-4" /> : <PowerOff className="mr-2 h-4 w-4" />}
                    {selectedRule.is_enabled ? "Disable" : "Enable"}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => startEditingRule(selectedRule)} disabled={savingRuleId !== null}>
                    <Edit3 className="mr-2 h-4 w-4" />
                    Edit
                  </Button>
                  <Button type="button" variant="destructive" onClick={() => setDeleteTarget(selectedRule)} disabled={savingRuleId !== null}>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={deleteTarget !== null} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent className="overflow-hidden p-0 sm:max-w-md">
          <DialogHeader className="border-b border-border bg-destructive/5 px-6 py-5 pr-12">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                <Trash2 className="h-5 w-5" />
              </div>
              <DialogTitle className="text-xl">Delete AI rule?</DialogTitle>
            </div>
          </DialogHeader>
          <div className="px-6 py-5">
            <p className="text-sm leading-6 text-muted-foreground">
              This rule will stop applying to future AI generations and edits. This action cannot be undone.
            </p>
          </div>
          <div className="flex justify-end gap-2 border-t border-border bg-muted/20 px-6 py-4">
            <Button type="button" variant="outline" onClick={() => setDeleteTarget(null)} disabled={isDeletingRule}>
              Cancel
            </Button>
            <Button type="button" variant="destructive" onClick={handleConfirmDeleteRule} disabled={isDeletingRule}>
              {isDeletingRule ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete rule
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
