#!/usr/bin/env bash
# Bring up the full stack (Supabase + backend + frontend + real LaTeX) and run
# the Playwright smoke suite. Used by CI and locally (`make e2e`).
#
# Lanes:
#   default        AI mocked via tests/e2e/mock_openai.py (deterministic, free)
#   E2E_REAL_AI=1  live OpenAI via OPEN_AI_KEY (merge queue / nightly lane)
#
# Everything else is always real: Postgres+GoTrue (local stack), uvicorn,
# next start, and the GHCR LaTeX compiler on :2700.
set -euo pipefail
cd "$(dirname "$0")/.."

# Local dev uses the repo venv; CI installs into the system interpreter.
UVICORN=".venv/bin/uvicorn"
[ -x "$UVICORN" ] || UVICORN="uvicorn"

PGIDS=()
spawn() { # run a service in its own process group so cleanup kills the whole tree
  setsid "$@" &
  PGIDS+=($!)
}
cleanup() {
  for pgid in "${PGIDS[@]:-}"; do kill -TERM -- "-$pgid" 2>/dev/null || true; done
}
trap cleanup EXIT

wait_for() { # url, name, tries
  for _ in $(seq 1 "${3:-60}"); do
    curl -sfo /dev/null "$1" && return 0
    sleep 2
  done
  echo "ERROR: $2 did not become healthy at $1" >&2
  return 1
}

# --- Supabase stack env (same mapping as make dev-backend) ------------------
eval "$(supabase status -o env 2>/dev/null | grep -E '^[A-Z0-9_]+=')"
if [ -z "${DB_URL:-}" ]; then
  echo "ERROR: local Supabase stack not running ('make up' or 'supabase start' first)" >&2
  exit 1
fi
export SUPABASE_URL="$API_URL" \
       SUPABASE_PUBLISHABLE_KEY="$PUBLISHABLE_KEY" \
       SUPABASE_SECRET_KEY="$SECRET_KEY" \
       SUPABASE_SERVICE_ROLE_KEY="$SERVICE_ROLE_KEY" \
       SUPABASE_JWT_SECRET="$JWT_SECRET" \
       DATABASE_URL="$DB_URL" \
       LATEX_COMPILER_BASE_URL="http://127.0.0.1:2700" \
       ENVIRONMENT="development"

# --- LaTeX compiler (must already be running; CI starts the GHCR image) -----
wait_for http://127.0.0.1:2700/ "LaTeX compiler" 30

# --- AI lane -----------------------------------------------------------------
if [ "${E2E_REAL_AI:-0}" = "1" ]; then
  if [ -z "${OPEN_AI_KEY:-}" ]; then
    echo "ERROR: E2E_REAL_AI=1 requires OPEN_AI_KEY" >&2
    exit 1
  fi
  echo ">> real-AI lane: live OpenAI"
else
  echo ">> mocked-AI lane: starting OpenAI stub on :9010"
  export OPEN_AI_KEY="sk-e2e-stub" OPENAI_BASE_URL="http://127.0.0.1:9010/v1"
  spawn bash -c "$UVICORN tests.e2e.mock_openai:app --host 127.0.0.1 --port 9010 >/tmp/e2e-mock-openai.log 2>&1"
  wait_for http://127.0.0.1:9010/docs "OpenAI stub" 15
fi

# --- Backend ------------------------------------------------------------------
spawn bash -c "$UVICORN backend.main:app --host 127.0.0.1 --port 8000 >/tmp/e2e-backend.log 2>&1"
wait_for http://127.0.0.1:8000/health "backend" 30

# --- Frontend (production build, same-origin Supabase proxy) ------------------
export NEXT_PUBLIC_SUPABASE_URL="http://localhost:3000" \
       SUPABASE_LOCAL_PROXY_TARGET="$API_URL" \
       NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY="$PUBLISHABLE_KEY" \
       NEXT_PUBLIC_API_URL="http://localhost:8000" \
       API_URL="http://localhost:8000"
(cd frontend && rm -rf .next && npm run build >/tmp/e2e-frontend-build.log 2>&1)
spawn bash -c 'cd frontend && npm run start >/tmp/e2e-frontend.log 2>&1'
wait_for http://localhost:3000/ "frontend" 30

# --- Run the suite -------------------------------------------------------------
# Override PLAYWRIGHT to run the suite elsewhere (e.g. the official Playwright
# docker image on hosts missing browser system libs — see docs/local-dev.md).
cd frontend
${PLAYWRIGHT:-npx playwright} test "$@"
