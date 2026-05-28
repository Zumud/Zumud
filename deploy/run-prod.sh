#!/usr/bin/env bash
# Minimal production launcher for the Zumud API.
# Use this if you don't want to bother with systemd yet (e.g. inside tmux/screen):
#
#     tmux new -s zumud
#     ./deploy/run-prod.sh
#
# It loads .env, sets safe production defaults, and runs uvicorn with multiple
# workers. uvicorn will restart any worker that crashes; if the master itself
# dies, run it again under tmux/screen or, better, install the systemd unit.

set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

export ENVIRONMENT="${ENVIRONMENT:-production}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export SENTRY_TRACES_SAMPLE_RATE="${SENTRY_TRACES_SAMPLE_RATE:-0.1}"
export SENTRY_PROFILES_SAMPLE_RATE="${SENTRY_PROFILES_SAMPLE_RATE:-0.1}"

VENV_PY=".venv/bin/python"
if [[ ! -x "${VENV_PY}" ]]; then
    echo "ERROR: ${VENV_PY} not found. Create the venv first:"
    echo "    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

echo "Starting Zumud API"
echo "  ENVIRONMENT       = ${ENVIRONMENT}"
echo "  LOG_LEVEL         = ${LOG_LEVEL}"
echo "  WEB_CONCURRENCY   = ${WEB_CONCURRENCY}"
echo "  HOST:PORT         = ${HOST}:${PORT}"
echo

exec .venv/bin/uvicorn backend.main:app \
    --host "${HOST}" \
    --port "${PORT}" \
    --workers "${WEB_CONCURRENCY}" \
    --proxy-headers \
    --forwarded-allow-ips="*" \
    --timeout-keep-alive 30 \
    --log-level info
