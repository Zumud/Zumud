import { test, expect } from '@playwright/test'

// The one thin happy path: signup -> add resume -> tailor -> a real PDF
// compiles. LaTeX is never stubbed; the AI is a deterministic fixture unless
// the stack runs with E2E_REAL_AI=1 (merge queue / nightly).

const email = `e2e-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`
const password = 'e2e-password-1'

const RESUME_TEXT = `Jane Doe
Senior Platform Engineer, Berlin
Experience: Acme Corp (2019-2026) - built Python delivery pipelines, led five engineers.
Education: BSc Computer Science, TU Berlin (2016).
Skills: Python, TypeScript, PostgreSQL, Docker.`

const JOB_DESCRIPTION = `Acme Robotics is hiring a Senior Python Engineer in Berlin
to build reliable backend services. Requirements: 5+ years Python, PostgreSQL, CI/CD.`

test('signup, add resume, tailor, download a real PDF', async ({ page }) => {
  // --- Signup through the identifier-first modal ---------------------------
  await page.goto('/')
  await page.getByRole('button', { name: 'Get started free' }).first().click()
  await expect(page.getByRole('heading', { name: 'Welcome to Zumud' })).toBeVisible()

  await page.getByLabel('Email').fill(email)
  await page.getByRole('button', { name: 'Continue', exact: true }).click()

  // Unknown email -> create-account step (local stack signs in immediately).
  await page.getByRole('textbox', { name: 'Password' }).fill(password)
  await page.getByRole('button', { name: 'Create account' }).click()
  await page.waitForURL('**/dashboard', { timeout: 30_000 })

  // --- Add resume content in profile settings ------------------------------
  await page.goto('/profile')
  await page.getByPlaceholder('Your resume content here...').fill(RESUME_TEXT)
  await page.getByRole('button', { name: 'Save resume' }).click()
  await expect(page.getByText('Resume text updated successfully!')).toBeVisible({
    timeout: 60_000,
  })

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
