# Supabase Auth migration ("Continue with Google")

This describes how to roll out the migration from the old custom username/password
+ self-issued JWT auth to **Supabase Auth (GoTrue)**, which also adds
"Continue with Google". The code is already in the repo; the steps below are the
manual configuration + data migration + cutover that a maintainer performs.

## What changed in the code

- **Backend** verifies a Supabase access token (instead of a self-issued JWT) and
  maps it to the existing `public.users` row via a new `supabase_uid` column.
  - `backend/core/supabase_auth.py` — verifies the token (asymmetric via the
    project JWKS, or legacy HS256 via `SUPABASE_JWT_SECRET`).
  - `backend/api/auth.py` — `get_current_user` resolves/auto-provisions the user
    and keeps a **transitional fallback** that still accepts old app-issued
    tokens so existing sessions aren't dropped at cutover.
  - `POST /login` and `POST /users/signup` are retired (Supabase owns these now).
- **Frontend** uses `@supabase/ssr`: login/signup/Google via the Supabase client,
  a `/auth/callback` route, cookie-based sessions, and the proxy guards protected
  routes. The backend is still called with `Authorization: Bearer <supabase token>`.
- The integer `users.id` stays the internal id; all FKs, filesystem paths
  (keyed by `username`), and Stripe (keyed by `email`) are unchanged.

Internal id stays put; only the auth boundary changed. New users are provisioned
lazily on their first authenticated API call (creates the profile row + an empty
resume), which is what makes "Continue with Google" auto-create an account.

## Phase 0 — Provider + Supabase configuration (Dev first, then Prod)

Project refs: Dev `sdxruoegdjgbxernfocl`, Prod `jbofotxkjouvmckymasn`.

1. **Google Cloud Console** -> APIs & Services -> Credentials -> Create OAuth
   client ID -> Web application. Set the Authorized redirect URI to the Supabase
   callback for each project:
   - `https://sdxruoegdjgbxernfocl.supabase.co/auth/v1/callback`
   - `https://jbofotxkjouvmckymasn.supabase.co/auth/v1/callback`
   Copy the Client ID and Client secret.
2. **Supabase Dashboard -> Authentication -> Sign In / Providers -> Google**:
   enable, paste Client ID + secret. (Do this for Dev and Prod separately.)
3. **Authentication -> URL Configuration**:
   - Site URL: `https://zumud.com` (Dev: `http://localhost:3000`).
   - Redirect URLs (allow-list): `https://zumud.com/auth/callback`,
     `https://www.zumud.com/auth/callback`, `http://localhost:3000/auth/callback`.
4. **Authentication -> Email**: decide on "Confirm email".
   - To match the old UX (immediate login after sign-up), **disable** it.
   - Enabling it is more secure but means new email signups must confirm before
     logging in. The frontend handles both (shows a "check your email" message).
   - Bulk-imported users are pre-confirmed regardless (see Phase 3).
5. **Settings -> API -> Exposed schemas**: remove `public` so the Data API
   (PostgREST) is not reachable with the publishable key now in the browser.
   The backend talks to Postgres directly (SQLAlchemy) and storage via the
   service key, so nothing app-side breaks. This neutralizes the RLS-disabled
   exposure; writing RLS policies remains the longer-term hardening if you ever
   want the frontend to read data directly.
6. Note the project's **JWT signing key type** (Authentication -> ... -> JWT keys):
   - Asymmetric (ES256/RS256): leave `SUPABASE_JWT_SECRET` unset; the backend
     verifies against the JWKS derived from `SUPABASE_URL`.
   - Legacy symmetric (HS256): copy the JWT secret into `SUPABASE_JWT_SECRET`.

## Phase 1 — Database schema (manual SQL, Dev then Prod)

> Status: **applied 2026-06-20** to Dev (`sdxruoegdjgbxernfocl`) and Prod
> (`jbofotxkjouvmckymasn`). Kept here for reference / fresh environments.

The app manages schema via `create_all()` (no migrations), which does **not**
alter existing tables, so run this once per project (idempotent):

```sql
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS supabase_uid uuid;
ALTER TABLE public.users ALTER COLUMN password DROP NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_supabase_uid ON public.users (supabase_uid);
```

Email-quality audit (gating prerequisite for the import — every user to migrate
needs a unique, valid, non-null email since login becomes email-based):

```sql
SELECT
  count(*)                                                          AS total,
  count(*) FILTER (WHERE email IS NULL OR btrim(email) = '')        AS missing_email,
  count(*) FILTER (WHERE email IS NOT NULL
                   AND email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$') AS invalid_email
FROM public.users;

-- Duplicate emails (case-insensitive) that must be resolved before import:
SELECT lower(email) AS email, count(*)
FROM public.users
WHERE email IS NOT NULL
GROUP BY lower(email)
HAVING count(*) > 1
ORDER BY count(*) DESC;
```

## Phase 2 — Backend env

Add to `/opt/zumud/.env` (and your local `.env`):

```
# only if the project uses the legacy HS256 JWT secret; omit for asymmetric keys
SUPABASE_JWT_SECRET=<project jwt secret>
```

`SUPABASE_URL` is already set and is used to derive the JWKS + issuer.

## Phase 3 — Import existing users into Supabase Auth

> Status: **run 2026-06-20**. Dev: 4/4 linked. Prod: 92 linked (of 97 password
> users). The 5 skipped rows belong to 3 duplicate-email groups — Prod
> `public.users` ids `104 & 109`, `119 & 120`, `115 & 122` — which need manual
> dedupe (keep one row per email), after which re-running the import (idempotent)
> links the survivor. The 27 password-less Prod rows are not migratable by
> password; they can use "Continue with Google" (auto-linked by email) or a
> password reset.

The one-time import script (`backend/scripts/migrate_users_to_supabase_auth.py`)
reused existing bcrypt hashes so passwords kept working, pre-confirmed emails,
created the `auth.identities` row, and linked `public.users.supabase_uid`. It
was removed after the migration completed — recover it from git history if a
re-import is ever needed.

## Phase 4 — Frontend env (required for build)

`frontend/.env.production` (and local `.env`) must contain the publishable values
so `next build` and the browser client work:

```
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
```

## Phase 5 — Cutover & verification

Deploy backend + frontend together (manual deploy per `local-context.mdc`):

```bash
cd /opt/zumud/repo && git pull --ff-only
# requirements.txt unchanged (no new backend deps)
cd frontend && npm ci && npm run build
systemctl restart zumud-backend zumud-frontend
```

Verify:

- Existing user logs in with email + password (imported account).
- Brand-new email signup creates a profile + empty resume (auto-provision).
- "Continue with Google" creates an account on first use and reuses it after.
- All protected routes work; resume upload works after signup.
The transitional legacy-token fallback (`_user_from_legacy_token`, the
`pwd_context`/pwdlib block, and `SECRET_KEY`/`ALGORITHM`) was removed in July
2026 after the 30-day cutover window closed. `SECRET_KEY`/`ALGORITHM` can be
deleted from deployed `.env` files. Remaining optional contraction: drop the
now-unused `users.password` column.
