# Pull-based auto-deploy

Merging to `main` deploys to prod within ~10 minutes, with a health-checked
rollback. GitHub holds no prod credentials: the VPS pulls with its existing
read-only deploy key.

## Flow

Every 10 minutes, `zumud-deploy.timer` runs [zumud-deploy.sh](zumud-deploy.sh):

1. `git fetch` — exit quietly if `main` is unchanged (batching is inherent:
   one deploy picks up everything merged since the last tick).
2. `git merge --ff-only origin/main`, then rebuild only what changed:
   `requirements.txt` → pip install; `frontend/` → npm ci + build;
   `docker/latex/` → pull the new GHCR image; `migrations/` → `alembic
   upgrade head`.
3. Write `SENTRY_RELEASE=<sha>` to `/opt/zumud/release.env` and restart
   `zumud-backend` + `zumud-frontend`.
4. Health-check `/health` and the frontend for up to 60s. On failure:
   hard-reset to the previous commit, rebuild, restart, and mark the unit
   failed (visible in `systemctl status zumud-deploy` / journal; the external
   uptime monitor is the second net).

**Manual brake:** `touch /opt/zumud/deploy-paused` stops all deploys until
removed.

## One-time install (on the VPS, as root)

```bash
cd /opt/zumud/repo && sudo -u zumud git pull --ff-only

# Adopt Alembic (tables already exist from create_all):
sudo -u zumud -H bash -lc 'set -a; . /opt/zumud/.env; set +a; cd /opt/zumud/repo && .venv/bin/pip install -r requirements.txt && .venv/bin/alembic stamp head'

# Sentry release tagging: add to BOTH service units ([Service] section):
#   EnvironmentFile=-/opt/zumud/release.env
systemctl edit zumud-backend    # add the line above
systemctl edit zumud-frontend   # add the line above

# Switch the LaTeX container to the GHCR image (was a hand-built local tag):
docker pull ghcr.io/zumud/zumud-latex:latest
docker rm -f zumud-latex
docker run -d --name zumud-latex --restart unless-stopped -p 127.0.0.1:2700:2700 ghcr.io/zumud/zumud-latex:latest

# Install the deployer:
ln -sf /opt/zumud/repo/deploy/zumud-deploy.service /etc/systemd/system/
ln -sf /opt/zumud/repo/deploy/zumud-deploy.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now zumud-deploy.timer

# Verify:
systemctl start zumud-deploy.service && journalctl -u zumud-deploy -n 20
```
