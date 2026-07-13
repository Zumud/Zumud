# SEO Guidelines

Per-PR rules for anything that touches Zumud's public web surface. The CI SEO
gate (`scripts/seo_gate.py`) reads this file verbatim and judges PRs against
it — evolving these rules is just editing this doc. Keep it short; the
strategy and rationale live in [`seo-strategy.md`](seo-strategy.md).

## Code rules (public pages, metadata, crawl surface)

1. Every public page exports a unique `title`, `description`, and canonical
   URL (via `metadata` or `generateMetadata`).
2. Private/app pages (`/dashboard`, `/profile`, `/history`, `/resume/*`,
   auth flows) stay `robots: { index: false, follow: false }`. Never noindex
   a public page.
3. A new public page is added to `frontend/src/app/sitemap.ts` and
   `frontend/public/llms.txt` in the same PR that creates it.
4. Do not block search or AI crawlers (Googlebot, Bingbot, GPTBot,
   OAI-SearchBot, ClaudeBot, PerplexityBot) in `robots.ts` or headers.
5. Open Graph / Twitter images are PNG or JPG (1200x630), never SVG.
6. User-visible marketing/content text must be present in the server-rendered
   HTML — not injected client-side after load and not behind auth.
7. Facts must be consistent everywhere they appear: pricing, claims, and
   feature descriptions must match between page copy and JSON-LD.
8. JSON-LD must describe what is actually on the page — no fabricated
   ratings, reviews, or dates.

## Content rules (guides, landing copy)

9. Answer-first: each H2 is a question a reader would ask; the first
   40–60 words under it answer that question directly.
10. Fact-dense: concrete numbers with named, linked sources; attributed
    quotes over vague claims. No invented statistics.
11. Content pages show a visible published date and last-updated date, and
    carry matching `datePublished`/`dateModified` in their Article JSON-LD.
12. Short paragraphs (2–4 sentences); use tables for comparisons; end with a
    FAQ block carrying FAQPage schema when the topic warrants it.
13. Write for the reader, not the crawler: no keyword stuffing, no filler
    intros, no near-duplicate pages targeting keyword variants.
14. Guide MDX frontmatter must include `title`, `description`,
    `datePublished`, and `dateModified`.
