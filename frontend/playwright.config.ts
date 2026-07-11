import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  // PDF generation through real LaTeX (and optionally a live model) is slow.
  timeout: 240_000,
  // One retry absorbs provider hiccups in the real-AI lane and CI flakes.
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI
    ? [['github'], ['html', { open: 'never' }]]
    : [['list']],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'retain-on-failure',
  },
})
