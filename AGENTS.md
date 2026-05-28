# Agent Context — Zumud

AI resume / cover-letter tailoring. FastAPI + Next.js 15 + Supabase Postgres. Self-hosted on a single VPS behind Cloudflare.

> A second file at `.cursor/rules/local-context.mdc` may exist on a maintainer's machine with deployment specifics and current production posture. It is gitignored; do not assume contributors have it.

## Stack

| | Tech | Notes |
|---|---|---|
| Frontend | Next.js 15 (App Router) + React 19 + Tailwind 4 | `next start` behind Caddy |
| Backend | FastAPI / uvicorn, SQLAlchemy 2 | 2 workers in prod |
| DB | Supabase Postgres | Custom username/password auth in `users.password` (bcrypt); `auth.users` is unused |
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
.venv/bin/uv pip install -r requirements.txt
.venv/bin/uvicorn backend.main:app --reload     # :8000

cd frontend && npm ci && npm run dev             # :3000
```

For local PDF generation, either run the LaTeX compiler container locally:
```
docker run -d --name zumud-latex -p 127.0.0.1:2700:2700 <your-built-image>
```
…or SSH-tunnel to a remote one. Either way, the backend defaults `LATEX_COMPILER_BASE_URL` to `http://127.0.0.1:2700` so no env change is needed.

## Conventions & gotchas

- **Schema is managed by `Base.metadata.create_all()` at startup.** No Alembic, no migration history. Adding a column = nullable + backfill manually. Modifying or dropping a column = manual SQL.
- **Supabase storage is write-only in the code.** No `download` / `list` / `get_signed_url` calls anywhere. All user-facing PDFs/TeX/JSON are served from local `/Applications/` on the deploy host. The bucket is effectively a write-only archive.
- **`next.config.ts` silences ESLint and TS errors at build time** (`ignoreDuringBuilds`, `ignoreBuildErrors`). Real bugs will ship if you rely on the build to catch them.
- **CORS is `allow_origins=["*"]`** in `backend/main.py` — intentional during launch; tighten before adding cross-origin-sensitive endpoints.
- **Upstream `aslushnikov/latex-online` is abandoned.** Don't `docker pull` it — we maintain our own image. Source for the modified Dockerfile lives under `~/latex-online-src/` on the deploy host.
- **`requirements.txt` carries unused `streamlit` and `altair`** (~150 MB) — backend doesn't import them. Safe to drop next time the file is touched.

## Process management

Three systemd-managed services on the VPS:
- `zumud-backend` — uvicorn, 127.0.0.1:8000
- `zumud-frontend` — `next start`, 127.0.0.1:3000
- `caddy` — TLS reverse proxy on 80/443

The LaTeX compiler runs as a docker container `zumud-latex` on 127.0.0.1:2700 (not systemd).

Standard deploy:
```
cd /opt/zumud/repo && git pull --ff-only
.venv/bin/pip install -r requirements.txt        # only if requirements.txt changed
cd frontend && npm ci && npm run build           # only if frontend/ changed
systemctl restart zumud-backend zumud-frontend
```

## Backlog

A maintainer roadmap is tracked separately (see `.cursor/rules/local-context.mdc` if available). High-level themes, roughly in priority order: external monitoring, feature flags (billing, cloud-backup), RLS policies on user tables, CORS lockdown, replace abandoned latex-online upstream, introduce Alembic.
