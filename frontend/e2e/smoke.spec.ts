import { test, expect, type Page } from '@playwright/test'

// Two thin happy paths: signup -> add resume -> tailor -> a real PDF compiles, and
// uploading a .tex that becomes a template the user can pick. LaTeX is never stubbed;
// the AI is a deterministic fixture unless the stack runs with E2E_REAL_AI=1 (merge
// queue / nightly).

const password = 'e2e-password-1'

function newEmail() {
  return `e2e-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`
}

const email = newEmail()

const RESUME_TEXT = `Jane Doe
Senior Platform Engineer, Berlin
Experience: Acme Corp (2019-2026) - built Python delivery pipelines, led five engineers.
Education: BSc Computer Science, TU Berlin (2016).
Skills: Python, TypeScript, PostgreSQL, Docker.`

const JOB_DESCRIPTION = `Acme Robotics is hiring a Senior Python Engineer in Berlin
to build reliable backend services. Requirements: 5+ years Python, PostgreSQL, CI/CD.`

// An ordinary LaTeX resume, no Jinja anywhere — the kind of file a user actually has.
// Its preamble is frozen and reattached verbatim, so what the stubbed model returns
// (tests/e2e/mock_openai.py) has to compile against exactly this setup.
const UPLOAD_TEX = String.raw`\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\pagestyle{empty}

\begin{document}
\begin{center}
{\LARGE \textbf{Ada Lovelace}}
\\ ada@example.com
\end{center}

\section*{Experience}
\noindent \textbf{Analytical Engine Project} --- Mathematician \hfill 1842 -- 1843
\par
\begin{itemize}
\item Wrote the first published algorithm intended for a machine.
\end{itemize}
\end{document}
`

// Signup through the identifier-first modal. Unknown email -> create-account step,
// which the local stack signs in immediately.
async function signUp(page: Page, address: string) {
  await page.goto('/')
  await page.getByRole('button', { name: 'Get started free' }).first().click()
  await expect(page.getByRole('heading', { name: 'Welcome to Zumud' })).toBeVisible()

  await page.getByLabel('Email or username').fill(address)
  await page.getByRole('button', { name: 'Continue', exact: true }).click()

  await page.getByRole('textbox', { name: 'Password' }).fill(password)
  await page.getByRole('button', { name: 'Create account' }).click()
  await page.waitForURL('**/dashboard', { timeout: 30_000 })
}

test('signup, add resume, tailor, download a real PDF', async ({ page }) => {
  await signUp(page, email)

  // Dashboard navigation should only expose active destinations, and the
  // Zumud wordmark should link back to the landing page.
  await page.getByRole('button', { name: 'Expand sidebar' }).click()
  await expect(page.getByRole('button', { name: 'Manage Subscription' })).toHaveCount(0)
  await expect(page.getByRole('link', { name: 'Go to Zumud home page' })).toHaveAttribute('href', '/')

  // Landing CTAs must reflect the active session and must not reopen auth.
  await page.goto('/')
  await expect(page.getByRole('link', { name: 'Dashboard' }).first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Open resume form' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Get started free' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Sign in' })).toHaveCount(0)

  // --- Add resume content in profile settings ------------------------------
  await page.goto('/profile')
  await page.getByPlaceholder('Your resume content here...').fill(RESUME_TEXT)
  await page.getByRole('button', { name: 'Save resume' }).click()
  await expect(page.getByText('Resume text updated successfully.')).toBeVisible({
    timeout: 60_000,
  })

  // The template gallery lists the built-ins and shows which one generation will
  // actually use. Its thumbnail is a committed asset, so a 404 here means the
  // preview was never rendered for a template the registry offers.
  const mteck = page.getByRole('button', { name: /MTeck/ })
  await expect(mteck).toBeVisible()
  await expect(mteck.getByText('In use')).toBeVisible()
  const preview = await page.request.get('/templates/mteck.png')
  expect(preview.status()).toBe(200)

  // --- Tailor against a job description and get a real compiled PDF --------
  await page.goto('/dashboard')
  await page
    .getByPlaceholder(/Paste the job description here/)
    .fill(JOB_DESCRIPTION)

  // A LaTeX compile failure raises a 500 in the backend, so a 200 here means
  // a PDF genuinely compiled.
  const pdfResponse = page.waitForResponse(
    (response) =>
      response.url().includes('/applications/resume/pdf') &&
      response.status() === 200,
    { timeout: 210_000 },
  )
  await page.getByRole('button', { name: /Generate Resume/ }).click()
  await expect(page.getByRole('region', { name: 'Resume generation progress' })).toBeVisible()
  await expect(page.getByText('Preparing your resume')).toBeVisible()
  const response = await pdfResponse

  expect(response.headers()['content-type']).toContain('application/pdf')
  // A real page weighs tens of KB; an error blob wouldn't.
  expect(Number(response.headers()['content-length'])).toBeGreaterThan(5_000)

  // The UI reaches its success state: the results panel with the PDF viewer
  // and its action buttons (never rendered on the error path).
  await expect(page.getByRole('button', { name: /Overleaf/ })).toBeVisible({
    timeout: 30_000,
  })
})

test('upload a .tex and it becomes a template you can pick', async ({ page }) => {
  await signUp(page, newEmail())
  await page.goto('/profile')

  const dropzone = page.locator('input[type="file"][accept=".tex"]')

  // Refused before it costs a conversion, without a round trip.
  await dropzone.setInputFiles({
    name: 'resume.pdf',
    mimeType: 'application/pdf',
    buffer: Buffer.from('%PDF-1.4 not really'),
  })
  await expect(page.getByText('Upload the .tex source of your resume.')).toBeVisible()

  await dropzone.setInputFiles({
    name: 'ada-resume.tex',
    mimeType: 'text/x-tex',
    buffer: Buffer.from(UPLOAD_TEX),
  })

  // Accepted, not created: the request returns while the conversion runs, so the
  // template arrives unusable and the page has to notice when that changes.
  const uploaded = page.getByRole('button', { name: 'Use the ada-resume template' })
  await expect(uploaded).toBeVisible()
  await expect(uploaded).toBeDisabled()
  await expect(page.getByText(/Converting your LaTeX/)).toBeVisible()

  // Conversion renders the candidate against both reference resumes and compiles
  // each with real LaTeX, so becoming selectable is proof it produced a PDF.
  await expect(uploaded).toBeEnabled({ timeout: 180_000 })
  await uploaded.click()
  await expect(uploaded.getByText('In use')).toBeVisible()

  // Removing the template in use hands generation back to a built-in rather than
  // leaving it pointed at a row that no longer exists.
  await page.getByRole('button', { name: 'Remove ada-resume' }).click()
  await page.getByRole('button', { name: 'Remove for good' }).click()
  await expect(page.getByText('Template removed.')).toBeVisible()
  await expect(uploaded).toHaveCount(0)
  await expect(
    page.getByRole('button', { name: /Use the MTeck/ }).getByText('In use'),
  ).toBeVisible()
})
