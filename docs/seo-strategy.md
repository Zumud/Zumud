# SEO + LLM Discoverability Strategy

How Zumud gets found — via Google and via AI answer engines (ChatGPT,
Perplexity, Gemini, Copilot). This is the living playbook; update it as we
learn what works. The enforceable per-PR rules live in
[`seo-guidelines.md`](seo-guidelines.md) (read by the CI SEO gate).

## How discovery works (2026)

- **ChatGPT** retrieves live results through **Bing's index** (not Google's)
  and recommends brands it sees named consistently across independent sources
  (editorial articles, Wikipedia/Wikidata, review sites). Bing indexing is a
  hard prerequisite.
- **Perplexity** is citation-first and freshness-first: its own crawler
  (PerplexityBot) plus heavy weighting of Reddit/Quora/forums (~40–50% of
  commercial-intent citations) and content published in the last 30 days.
- **Google** AI Overviews build on the normal Google index; classic SEO still
  applies.
- Across all engines, the content that gets cited is **answer-first and
  fact-dense** (statistics, attributed claims), with clear heading structure
  and JSON-LD.

Implication: the technical baseline matters, but the real levers are
(a) content that directly answers the questions job-seekers ask, and
(b) corroboration — independent mentions the engines can triangulate.

## In the codebase

Done:

- Dynamic `frontend/src/app/robots.ts` + `sitemap.ts` (AI crawlers explicitly
  allowed), `frontend/public/llms.txt`, PNG OG images, JSON-LD
  (Organization/WebSite/SoftwareApplication in the root layout, FAQPage on the
  landing FAQ), `noindex` on all app/private pages, custom 404.

Next (in rough order):

1. **Guides section** (`/guides/[slug]`, MDX in-repo, no CMS): shared layout
   emitting `generateMetadata`, Article + BreadcrumbList JSON-LD, author
   byline, visible published/updated dates. Guides get added to `sitemap.ts`
   and `llms.txt` in the same PR.
2. **Cornerstone content** (AI-drafted, maintainer-reviewed):
   - How to tailor your resume to a job description (head topic)
   - What makes a resume ATS-friendly (and what breaks parsing)
   - LaTeX resumes: why they parse cleanly + free templates
   - Resume tailoring: manual vs AI tools compared (honest, names competitors)
   - How many applications does it take to get an interview (statistics
     roundup — the citation-bait piece)
3. Cadence: ~1–2 guides/month; quarterly freshness pass updating stats and
   `dateModified` on existing pages (stale pages lose AI citations).
4. Later: free standalone tools (ATS-check, keyword-match widget) — earn
   backlinks better than articles. Defer until guides are live.

Deliberately skipped: i18n/hreflang, CMS, programmatic page generation
(thin auto-generated pages hurt in 2026), paid SEO tooling.

## Off-site checklist (maintainer, in order of leverage)

1. [ ] **Bing Webmaster Tools** — verify domain, submit sitemap, confirm
       indexing. This is the gateway to ChatGPT retrieval. Also Google Search
       Console if not already set up.
2. [ ] **Entity foundations** — Wikidata entry; consistent name/description/
       logo on the GitHub org, LinkedIn company page, Crunchbase.
3. [ ] **Directories & reviews** — Product Hunt launch, AlternativeTo,
       There's An AI For That, G2/Capterra. These listicle pages are exactly
       what LLMs retrieve for "best resume tools" queries.
4. [ ] **Open-source angle** — awesome-lists (awesome-selfhosted, job-search
       tool lists), Hacker News "Show HN". The GitHub README is itself a
       crawled entity signal.
5. [ ] **Community presence** — genuine participation in r/resumes, r/jobs,
       r/EngineeringResumes, relevant Quora questions. Mention Zumud only
       where it truly fits; planted/fake posts backfire.
6. [ ] **Earned mentions** — pitch the statistics guide to job-search
       newsletters/blogs. Target 5–10 quality mentions, not mass link
       building.

## Measurement loop (monthly)

- **AI referrals**: PostHog segment on referrers `chatgpt.com`,
  `perplexity.ai`, `gemini.google.com`, `copilot.microsoft.com`.
- **Search consoles**: GSC + Bing WMT — impressions, queries, index coverage.
- **Citation spot-check**: run the query list below against ChatGPT,
  Perplexity, and Google; record whether Zumud is mentioned/cited. Manual at
  first; automatable later via the OpenAI/Perplexity APIs.

### Query list

1. best AI resume tailoring tool
2. ATS friendly resume builder
3. LaTeX resume generator online
4. how to tailor my resume to a job description
5. AI tool to customize resume for each job
6. free resume tailoring tool
7. open source resume builder
8. resume builder that exports LaTeX / Overleaf
9. AI cover letter generator from job posting
10. how to get past ATS resume screening
11. best resume format for ATS 2026
12. Zumud review / is Zumud legit
13. alternatives to [top competitor in results]
14. tool to match resume keywords to job description
15. how many job applications to get an interview

Log results and observations below as dated bullet points.

### Findings log

- (none yet)
