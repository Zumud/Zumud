import { expect, test, type Page, type Route } from '@playwright/test'

const jobDescription = `A product company is hiring a senior software engineer.
The role requires TypeScript, Python, PostgreSQL, and distributed systems experience.`
const password = 'e2e-password-1'

async function signUp(page: Page) {
  const email = `progress-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.com`
  await page.goto('/')
  await page.getByRole('button', { name: 'Get started free' }).first().click()
  await page.getByLabel('Email or username').fill(email)
  await page.getByRole('button', { name: 'Continue', exact: true }).click()
  await page.getByRole('textbox', { name: 'Password' }).fill(password)
  await page.getByRole('button', { name: 'Create account' }).click()
  await page.waitForURL('**/dashboard', { timeout: 30_000 })
}

async function respondAfterAnimationStarts(
  route: Route,
  options: Parameters<Route['fulfill']>[0],
) {
  await new Promise((resolve) => setTimeout(resolve, 750))
  await route.fulfill(options)
}

async function expectProgressLifecycle(page: Page, accessibleName: string, firstStep: string) {
  const progress = page.getByRole('region', { name: accessibleName })
  await expect(progress).toBeVisible()
  await expect(progress.getByText(new RegExp(`Current step: ${firstStep}`))).toBeVisible()
  await expect(progress).toHaveCount(0, { timeout: 5_000 })
}

test('generation progress restarts and closes for every dashboard output', async ({ page }) => {
  await page.route('**/applications/resume/pdf?**', (route) =>
    respondAfterAnimationStarts(route, {
      status: 200,
      contentType: 'application/pdf',
      headers: { 'Content-Disposition': 'attachment; filename="resume.pdf"' },
      body: Buffer.from('%PDF-1.4\n%%EOF'),
    }),
  )
  await page.route('**/applications/resume/json', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.route('**/applications/cover-letter/plain?**', (route) =>
    respondAfterAnimationStarts(route, {
      status: 200,
      contentType: 'text/plain',
      body: 'A focused cover letter.',
    }),
  )
  await page.route('**/applications/questions/answer?**', (route) =>
    respondAfterAnimationStarts(route, {
      status: 200,
      contentType: 'text/plain',
      body: 'A focused application answer.',
    }),
  )

  await signUp(page)
  const jobDescriptionInput = page.getByPlaceholder(/Paste the job description here/)
  await jobDescriptionInput.fill(jobDescription)

  await page.getByRole('button', { name: /Generate Resume/ }).click()
  await expectProgressLifecycle(page, 'Resume generation progress', 'Review role')

  await jobDescriptionInput.fill(`${jobDescription}\nCloud experience is preferred.`)
  await page.getByRole('button', { name: /Generate Resume/ }).click()
  await expectProgressLifecycle(page, 'Resume generation progress', 'Review role')

  await page.getByRole('button', { name: /Generate Cover Letter/ }).click()
  await expectProgressLifecycle(page, 'Cover letter generation progress', 'Review role')

  await page.getByRole('button', { name: /Answer Question/ }).click()
  await page
    .getByPlaceholder(/Enter the application question/)
    .fill('Why are you a strong match for this role?')
  await page.getByRole('button', { name: /Generate Your Tailored Answer/ }).click()
  await expectProgressLifecycle(page, 'Answer generation progress', 'Read question')
})
