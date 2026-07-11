#!/usr/bin/env bash
# Pull-based deployer — runs on the VPS from zumud-deploy.timer every 10 min.
# Pulls origin/main, rebuilds only what changed, migrates, restarts, health-
# checks, and rolls back to the previous commit on failure. GitHub never
# holds prod credentials; the box pulls with its read-only deploy key.
#
# Pause deploys (the manual brake): touch /opt/zumud/deploy-paused
set -euo pipefail

REPO=/opt/zumud/repo
ENV_FILE=/opt/zumud/.env
RELEASE_ENV=/opt/zumud/release.env
PAUSE_FILE=/opt/zumud/deploy-paused
BACKEND_HEALTH=http://127.0.0.1:8000/health
FRONTEND_URL=http://127.0.0.1:3000/
LATEX_IMAGE=ghcr.io/zumud/zumud-latex:latest

as_zumud() {
  sudo -u zumud -H bash -lc \
    "export GIT_SSH_COMMAND='ssh -i /opt/zumud/.ssh/id_ed25519 -o UserKnownHostsFile=/opt/zumud/.ssh/known_hosts'; cd $REPO && $*"
}

log() { echo "[zumud-deploy] $*"; }

health_check() {
  for _ in $(seq 1 15); do
    if curl -sf "$BACKEND_HEALTH" >/dev/null && curl -sfo /dev/null "$FRONTEND_URL"; then
      return 0
    fi
    sleep 4
  done
  return 1
}

build_and_restart() { # $1 = space-separated list of changed paths
  local changed="$1"
  if grep -q '^requirements.txt' <<<"$changed"; then
    log "requirements.txt changed -> pip install"
    sudo -u zumud "$REPO/.venv/bin/pip" install -q -r "$REPO/requirements.txt"
  fi
  if grep -q '^docker/latex/' <<<"$changed"; then
    log "docker/latex changed -> pulling new image"
    docker pull "$LATEX_IMAGE"
    docker rm -f zumud-latex || true
    docker run -d --name zumud-latex --restart unless-stopped \
      -p 127.0.0.1:2700:2700 "$LATEX_IMAGE"
  fi
  if grep -q '^frontend/' <<<"$changed"; then
    log "frontend changed -> npm ci && build"
    as_zumud "cd frontend && npm ci --no-audit --no-fund && npm run build"
  fi
  if grep -q '^migrations/' <<<"$changed"; then
    log "migrations changed -> alembic upgrade head"
    sudo -u zumud -H bash -lc \
      "set -a; . $ENV_FILE; set +a; cd $REPO && .venv/bin/alembic upgrade head"
  fi
  # Sentry release tagging: the SDK reads SENTRY_RELEASE from this file
  # (EnvironmentFile in both service units).
  echo "SENTRY_RELEASE=$(as_zumud 'git rev-parse --short HEAD')" > "$RELEASE_ENV"
  systemctl restart zumud-backend zumud-frontend
}

main() {
  if [ -f "$PAUSE_FILE" ]; then
    log "paused ($PAUSE_FILE exists) — skipping"
    return 0
  fi

  as_zumud "git fetch origin main --quiet"
  local current remote
  current=$(as_zumud "git rev-parse HEAD")
  remote=$(as_zumud "git rev-parse origin/main")

  if [ "$current" = "$remote" ]; then
    return 0
  fi

  log "deploying $current -> $remote"
  local changed
  changed=$(as_zumud "git diff --name-only HEAD origin/main")

  as_zumud "git merge --ff-only origin/main --quiet"
  build_and_restart "$changed"

  if health_check; then
    log "deploy OK at $remote"
    return 0
  fi

  log "HEALTH CHECK FAILED — rolling back to $current"
  as_zumud "git reset --hard $current --quiet"
  build_and_restart "$changed"

  if health_check; then
    log "rollback OK at $current — deploys need attention (unit marked failed)"
  else
    log "ROLLBACK ALSO UNHEALTHY — manual intervention required"
  fi
  return 1
}

main "$@"
