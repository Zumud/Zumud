# Local development & testing

A complete local stack via the **Supabase CLI** (Postgres + Auth/GoTrue + Storage +
Mailpit email catcher) so features — including the full auth flow — can be developed
and tested locally before anything ships. No cloud project required; the database is
plain Postgres you can point any tool at.

## Prerequisites
- Docker, the [Supabase CLI](https://supabase.com/docs/guides/cli), Node 20+, a Python 3.12
  venv at `.venv` (`python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt`;
  no 3.12 on your system? `uv python install 3.12` gives you one without touching system Python).
- snap-Docker note: the socket must be group `docker`. If `docker ps` is denied:
  `sudo chown root:docker /var/run/docker.sock` (and you're in the `docker` group).
  After joining the group, start a fresh login shell so it's active — otherwise prefix
  Docker-touching `make` targets with `sg docker -c "..."` (e.g. `sg docker -c "make up"`).

## Bring it up

```
make up            # start the Supabase stack (API :54321, DB :54322, Studio :54323, Mailpit :54324)
make dev-backend   # FastAPI on :8000 wired to the local stack   (one terminal)
make dev-frontend  # Next.js on :3000 wired to the local stack   (another terminal)
make seed          # optional: create a confirmed test user
make reset         # wipe + recreate the local DB
make down          # stop the stack
```

- App tables are created by SQLAlchemy `create_all()` on first backend connect, so the
  local schema matches prod with no manual SQL.
- `make dev-backend` reads the local creds from `supabase status` and exports them ahead
  of uvicorn (they override the committed cloud `.env`). The only secret you supply is
  `OPEN_AI_KEY` in `.env`.
- `make dev-frontend` auto-creates `frontend/.env.local` from the local stack on first run
  (deterministic local keys, no secrets), so a fresh clone needs no manual frontend config.

## Testing auth locally
- The browser talks to Supabase **through the Next dev server** (same-origin): the
  browser client uses `http://localhost:3000` and Next proxies `/auth/v1/*` to the local
  stack, because the Docker-published Supabase port isn't reachable from the host browser
  under WSL. `frontend/.env.local` sets this up; server-side code uses the direct URL.
  Production is unaffected (it uses the real Supabase URL on both sides).
- Email confirmations are **off locally** (`enable_confirmations = false` in
  `supabase/config.toml`) so signup signs you in immediately — the confirmation link and
  Mailpit live on Docker ports the host browser can't reach. Production keeps
  confirmations on (configured in the Supabase dashboard).
- Local tokens are **ES256 (JWKS)**, same as prod; the backend verifies them identically.
  Any emails that do get sent (e.g. password reset) land in **Mailpit**
  (http://127.0.0.1:54324, reachable from WSL). Studio (DB browser): http://127.0.0.1:54323.
- Verified loop: signup -> instant session -> backend `/users/me` 200 (user lazily
  provisioned), and unauthenticated -> 401.

## Google sign-in locally (optional)
Add `http://127.0.0.1:54321/auth/v1/callback` to the Google OAuth client's authorized
redirect URIs. Local Google creds live in `supabase/.env.local` (gitignored).

## PDF generation (LaTeX)
Resume / cover-letter PDFs are compiled by a local LaTeX service on `127.0.0.1:2700`
(the backend defaults `LATEX_COMPILER_BASE_URL` there). It's the same image as prod —
TeX Live 2024 + latex-online — built from `docker/latex/`:

```
make latex-up      # build (first run, ~4-5GB base pull) + start the compiler
make latex-down    # stop + remove it
```

The first compile lags ~30s while the container clones latex-online on startup. Auth and
most API flows need no LaTeX; only PDF generation does.

Alternative (no local build): tunnel `:2700` to a remote container —
`make latex-tunnel LATEX_SSH="-i ~/.ssh/id_ed25519 root@<host>"` (see
`.cursor/rules/local-context.mdc` for host/SSH options).
