import posthog from "posthog-js"

const key = process.env.NEXT_PUBLIC_POSTHOG_KEY

// Only enable analytics in production with a configured key. Locally it's pure
// noise — the key is invalid/blocked and the requests just error in the console.
if (key && process.env.NODE_ENV === "production") {
  posthog.init(key, {
    api_host: "/ingest",
    ui_host: "https://eu.posthog.com",
    defaults: '2025-05-24',
    capture_exceptions: true,
    debug: false,
  })
}
