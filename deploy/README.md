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
   `migrations/` → `alembic upgrade head`.
3. Make the LaTeX container run the image built from this commit, pinned to that
   commit's own tag rather than `:latest` — publishing takes minutes, so `:latest`
   can still be the previous build when the deploy fires. A tag that is not
   published yet leaves the running container alone and is retried next tick. A new
   image is only kept once it has actually compiled a document under both pdflatex
   and xelatex; otherwise the previous image goes back and the unit fails, because
   rolling the code back cannot fix a broken compiler.
4. Write `SENTRY_RELEASE=<sha>` to `/opt/zumud/release.env` and restart
   `zumud-backend` + `zumud-frontend`.
5. Health-check `/health` and the frontend for up to 60s. On failure:
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

# Install the deployer (it owns the LaTeX container from here — image, resource
# limits, and all — so there is nothing to start by hand):
ln -sf /opt/zumud/repo/deploy/zumud-deploy.service /etc/systemd/system/
ln -sf /opt/zumud/repo/deploy/zumud-deploy.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now zumud-deploy.timer

# Verify:
systemctl start zumud-deploy.service && journalctl -u zumud-deploy -n 20
```
