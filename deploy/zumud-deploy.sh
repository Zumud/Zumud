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
LATEX_IMAGE=ghcr.io/zumud/zumud-latex
# The compiler runs whatever LaTeX a user's template contains, so cap what a
# runaway document can consume. TeX has no execution limits of its own: an
# accidental \def loop will otherwise eat the box.
LATEX_RUN_OPTS="--memory=2g --cpus=2 --pids-limit=256 --security-opt=no-new-privileges"

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

alembic_() { # $1 = subcommand
  sudo -u zumud -H bash -lc \
    "set -a; . $ENV_FILE; set +a; cd $REPO && .venv/bin/alembic $1"
}

sync_migrations() {
  # "The schema is at this checkout's head" is an invariant, not something a diff
  # implies. Running alembic only when migrations/ appeared in the deploy's own diff
  # meant a migration that failed once was never retried: the failure aborted the
  # deploy with the merge already done, so the next tick saw nothing to deploy, and
  # every later diff no longer mentioned migrations/. On 2026-08-03 that left prod a
  # revision behind code that selected a column the migration adds, and the template
  # gallery raised for every user for five hours while the deploys all reported OK.
  local at
  at=$(alembic_ "current" 2>/dev/null | tail -1)
  case "$at" in
    *"(head)") return 0 ;;
  esac

  log "schema at ${at:-nothing} -> upgrading to head"
  alembic_ "upgrade head"
}

wanted_latex_image() {
  # The image is published per commit that touches docker/latex/, tagged with the
  # first 12 characters of that commit (.github/workflows/latex-image.yml). So the
  # image this checkout wants is the one built from its most recent such commit.
  local sha
  sha=$(as_zumud "git log -1 --format=%H -- docker/latex")
  echo "$LATEX_IMAGE:${sha:0:12}"
}

start_latex() { # $1 = image
  docker rm -f zumud-latex >/dev/null 2>&1 || true
  # shellcheck disable=SC2086 # LATEX_RUN_OPTS is a deliberate word list
  docker run -d --name zumud-latex --restart unless-stopped \
    $LATEX_RUN_OPTS -p 127.0.0.1:2700:2700 "$1" >/dev/null
  for _ in $(seq 1 30); do
    curl -sfo /dev/null http://127.0.0.1:2700/ && return 0
    sleep 2
  done
  return 1
}

latex_compiles() { # $1 = engine, $2 = extra preamble
  local dir status=1
  dir=$(mktemp -d)
  printf '\\documentclass{article}%s\\begin{document}ok\\end{document}\n' "$2" \
    > "$dir/probe.tex"
  tar -cf "$dir/probe.tar" -C "$dir" probe.tex
  if curl -sf --max-time 60 -F "file=@$dir/probe.tar;type=application/x-tar" \
      "http://127.0.0.1:2700/data?target=probe.tex&force=true&command=$1" \
      -o "$dir/probe.pdf" \
    && [ "$(head -c 5 "$dir/probe.pdf")" = "%PDF-" ]; then
    status=0
  fi
  rm -rf "$dir"
  return "$status"
}

sync_latex_image() {
  local want previous
  want=$(wanted_latex_image)
  previous=$(docker inspect zumud-latex -f '{{.Config.Image}}' 2>/dev/null || echo "")
  if [ "$want" = "$previous" ]; then
    return 0
  fi

  # Pinning to the commit's own tag closes a race that :latest cannot: publishing
  # takes minutes, so a deploy triggered by the very merge that changed the image
  # would otherwise pull one built from the previous commit. When the tag is not
  # published yet the pull simply fails, we keep serving the container we have, and
  # the next run finds the invariant still unmet and tries again.
  if ! docker pull -q "$want" >/dev/null; then
    log "WARN: $want not pullable yet — keeping ${previous:-none}, retrying next run"
    return 0
  fi

  log "LaTeX image -> $want"
  # Answering on the port is not the same as being able to compile — a missing
  # format file leaves the service up and every document failing — and pdflatex
  # working says nothing about xelatex, which templates using fontspec need.
  if start_latex "$want" \
    && latex_compiles pdflatex '' \
    && latex_compiles xelatex '\usepackage{fontspec}'; then
    return 0
  fi

  # Rolling the code back cannot fix a broken compiler, so the useful response is
  # to put the container that was working back, and let the unit fail loudly.
  log "ERROR: $want cannot compile — restoring ${previous:-none}"
  if [ -n "$previous" ]; then
    start_latex "$previous" || log "ERROR: $previous did not come back either"
  fi
  return 1
}

# Returns non-zero if any step failed, which the caller turns into a rollback. Every
# fallible step says so explicitly: the caller tests this function, and being tested
# suspends set -e for everything it runs, so an unchecked failure would fall through
# to the restart instead of stopping the deploy.
build_and_restart() { # $1 = space-separated list of changed paths
  local changed="$1"
  if grep -q '^requirements.txt' <<<"$changed"; then
    log "requirements.txt changed -> installing deps"
    if [ -x "$REPO/.venv/bin/pip" ]; then
      sudo -u zumud "$REPO/.venv/bin/pip" install -q -r "$REPO/requirements.txt" || return 1
    else
      # The prod venv is uv-managed (no pip inside).
      sudo -u zumud -H bash -lc \
        "cd $REPO && uv pip install -q -r requirements.txt --python .venv/bin/python" \
        || return 1
    fi
  fi
  # Before the frontend build, so a schema that cannot be brought up to date costs
  # seconds rather than the eight minutes of an npm build it would only invalidate.
  if ! sync_migrations; then
    log "MIGRATION FAILED — not restarting into a schema the code cannot use"
    return 1
  fi
  # Not gated on the changed paths: the invariant is "the container runs the image
  # built from this checkout", which also lets a deploy that could not pull earlier
  # heal itself on a later run, and restores the right image on a rollback.
  if ! sync_latex_image; then
    LATEX_SYNC_FAILED=1
  fi
  if grep -q '^frontend/' <<<"$changed"; then
    log "frontend changed -> npm ci && build"
    as_zumud "cd frontend && npm ci --no-audit --no-fund && npm run build" || return 1
  fi
  # Sentry release tagging: the SDK reads SENTRY_RELEASE from this file
  # (EnvironmentFile in both service units).
  echo "SENTRY_RELEASE=$(as_zumud 'git rev-parse --short HEAD')" > "$RELEASE_ENV"
  systemctl restart zumud-backend zumud-frontend || return 1
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
    # Nothing to deploy, but the invariants are still worth checking: an image pull
    # that failed on an earlier tick — the image was still building — and a schema
    # left behind by a migration that failed have to be able to heal here, rather
    # than waiting for the next commit to land.
    sync_migrations || return 1
    sync_latex_image || return 1
    return 0
  fi

  log "deploying $current -> $remote"
  local changed
  changed=$(as_zumud "git diff --name-only HEAD origin/main")

  as_zumud "git merge --ff-only origin/main --quiet"

  # A build step that fails has to roll back like a failed health check does. It did
  # not: set -e killed the script mid-deploy with the merge already committed, so the
  # tree stayed on the new commit, nothing was restarted, and the next tick saw
  # nothing left to deploy.
  if build_and_restart "$changed" && health_check; then
    if [ "${LATEX_SYNC_FAILED:-0}" = 1 ]; then
      log "deployed $remote, but the LaTeX image is stale — see ERROR above"
      return 1
    fi
    log "deploy OK at $remote"
    return 0
  fi

  log "DEPLOY FAILED — rolling back to $current"
  as_zumud "git reset --hard $current --quiet"
  build_and_restart "$changed" || true

  if health_check; then
    log "rollback OK at $current — deploys need attention (unit marked failed)"
  else
    log "ROLLBACK ALSO UNHEALTHY — manual intervention required"
  fi
  return 1
}

main "$@"
