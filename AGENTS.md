# Agent Context — Zumud

AI resume / cover-letter tailoring. FastAPI + Next.js 16 + Supabase Postgres. Self-hosted on a single VPS behind Cloudflare.

> A second file at `.cursor/rules/local-context.mdc` may exist on a maintainer's machine with deployment specifics and current production posture. It is gitignored; do not assume contributors have it.

## Stack

| | Tech | Notes |
|---|---|---|
| Frontend | Next.js 16 (App Router) + React 19 + Tailwind 4 | `next start` behind Caddy |
| Backend | FastAPI / uvicorn, SQLAlchemy 2 | 2 workers in prod |
| DB | Supabase Postgres | Auth via **Supabase Auth (GoTrue)**; `public.users` is the profile table (integer `id`) linked to `auth.users` by `supabase_uid` |
| LaTeX | Self-hosted `aslushnikov/latex-online` rebuild on `islandoftex/texlive:TL2024-historic` | Loopback-only on `127.0.0.1:2700` |
| Reverse proxy | Caddy + Let's Encrypt | |

## Repo layout

```
backend/
  main.py          # ASGI entry: backend.main:app
  models/          # SQLAlchemy models — db_models.py is the source of truth
  api/             # routers: auth, users, applications, billing
  core/            # ai_service, stripe_billing_service, storage_service
  config/          # envs, db, supabase client
frontend/          # Next.js app
docs/              # design docs, setup guides
requirements.txt   # Python deps (Python 3.12 target)
```

## Local dev

System Python on Ubuntu 26.04 is 3.14 and breaks several pinned wheels (notably `jiter`, `pydantic-core`, `psycopg2-binary`). Use Python **3.12** via `uv`:

```
.uv-python/cpython-3.12.*/bin/python3.12 -m venv .venv
.venv/bin/pip install -U pip uv
.venv/bin/uv pip install -r requirements-dev.txt
.venv/bin/uvicorn backend.main:app --reload     # :8000

cd frontend && npm ci && npm run dev             # :3000
```

Test lanes (see `docs/dev-pipeline.md` for the full pipeline):

```
make test              # unit lane: no DB, network, or secrets
make test-integration  # real local Supabase stack (make up first)
make e2e               # full-stack Playwright smoke (real LaTeX, stubbed AI)
pytest -m real_ai      # live-model contract tests (needs a real OPEN_AI_KEY)
```

For local PDF generation, either run the LaTeX compiler container locally:
```
docker run -d --name zumud-latex -p 127.0.0.1:2700:2700 <your-built-image>
```
…or SSH-tunnel to a remote one. Either way, the backend defaults `LATEX_COMPILER_BASE_URL` to `http://127.0.0.1:2700` so no env change is needed.

## Conventions & gotchas

- **Auth is Supabase Auth.** The frontend logs in via `@supabase/ssr` (email/password or "Continue with Google"); the backend verifies the Supabase access token (`backend/core/supabase_auth.py`) and maps it to a `public.users` row via `supabase_uid`. `get_current_user` **lazily provisions** a profile (+ empty resume) on first authenticated request, which is how Google sign-in auto-creates accounts. Login is by **email**; keep existing `username` values stable (filesystem paths key off them). `/login` and `/users/signup` are retired. See `docs/supabase-auth-migration.md` for the full rollout (provider config, schema SQL, user import, cutover).
- **Schema is managed by Alembic** (`migrations/`; expand/contract convention: add nullable → backfill → contract in a later PR). Any model change needs `alembic revision --autogenerate` in the same PR — CI runs a drift check (`scripts/migration-check.sh`) that fails otherwise. `Base.metadata.create_all()` still runs at startup purely so a fresh clone boots with zero setup; deployed environments migrate via `alembic upgrade head`.
- **Supabase storage is write-only in the code.** No `download` / `list` / `get_signed_url` calls anywhere. All user-facing PDFs/TeX/JSON are served from local `/Applications/` on the deploy host. The bucket is effectively a write-only archive.
- **`next.config.ts` sets `typescript.ignoreBuildErrors`** — real TS type errors still ship. (Next 16 decoupled ESLint from the build; run `npm run lint` separately.)
- **CORS** is restricted to the frontend origins via `CORS_ALLOWED_ORIGINS` (defaults to `https://zumud.com,https://www.zumud.com` in prod). Add new allowed origins there — do not revert to a wildcard (invalid with credentials anyway).
- **Upstream `aslushnikov/latex-online` is abandoned.** Don't `docker pull` it — we maintain our own image. Source for the modified Dockerfile lives under `~/latex-online-src/` on the deploy host.
- **`requirements.txt` is a full pinned freeze** (Python 3.12 target). Regenerate via `pip freeze` after dependency changes; the set is verified clean with `pip-audit`. Dev/CI-only tools live in `requirements-dev.txt`.
- **One purpose per PR; the gates are strict.** CI enforces ruff (+format), import-linter layering (`api -> core -> utils -> models -> config`), knip, diff-coverage on changed lines, secret/dependency scans, an AI scope-coherence gate judged against `.cursor/rules/principles.mdc`, and the full test lanes. `tier:T2` paths (deps, auth, billing, migrations, `.github/`, `deploy/`, `scripts/`) additionally need maintainer approval. See `docs/dev-pipeline.md`.

## Process management

Three systemd-managed services on the VPS:
- `zumud-backend` — uvicorn, 127.0.0.1:8000
- `zumud-frontend` — `next start`, 127.0.0.1:3000
- `caddy` — TLS reverse proxy on 80/443

The LaTeX compiler runs as a docker container `zumud-latex` on 127.0.0.1:2700 (not systemd), pulled from `ghcr.io/zumud/zumud-latex` (published by CI from `docker/latex/`).

**Deploys are automatic**: a systemd timer (`deploy/zumud-deploy.timer`) polls `origin/main` every 10 minutes, rebuilds only what changed, runs `alembic upgrade head`, restarts services, health-checks, and rolls back on failure. Merging to `main` is deploying. See `deploy/README.md` (manual brake: `touch /opt/zumud/deploy-paused`).

## Backlog

A maintainer roadmap is tracked separately (see `.cursor/rules/local-context.mdc` if available). High-level themes, roughly in priority order: external uptime monitoring, RLS policies on user tables, a `BILLING_ENABLED` feature flag, dropping legacy prod DB columns, and (optional) CI/CD + staging + Alembic.
