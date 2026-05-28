# Zumud production runbook

> **Reference document.** This describes a clean, hardened way to deploy the
> API. The canonical live setup may differ — see `AGENTS.md` for the actual
> deployment shape. Paths below assume the repo is cloned at `/opt/zumud`;
> on the current live deployment the repo lives at `/opt/zumud/repo` (the
> env file stays at `/opt/zumud/.env`). Substitute accordingly.

This document covers the things you need to do **on the server hosting
`api.zumud.com`** to stop the periodic Cloudflare 521s.

The 521 means Cloudflare reached the network but the origin TCP socket
refused/closed the connection. In practice that has three causes for this app:

1. The uvicorn process crashed and nothing restarted it.
2. The single uvicorn worker is blocked (long LaTeX compile / OpenAI call /
   Stripe call) and isn't accepting new TCP connections.
3. The VM ran out of resources (RAM, disk, file descriptors) — most often disk
   filled up by `log/` because of `LOG_LEVEL=DEBUG`.

The code changes in this PR address all three. You still need to apply config
on the server.

---

## 1. Pull the new code on the server

```bash
ssh <your-user>@<your-vps>
cd /opt/zumud           # or wherever the repo lives
git pull
.venv/bin/pip install -r requirements.txt
```

## 2. Update `.env` on the server

Set these (most important first):

```dotenv
ENVIRONMENT=production
LOG_LEVEL=INFO
WEB_CONCURRENCY=2          # number of uvicorn workers; 2 is fine for 1-2 vCPU
PORT=8000
HOST=0.0.0.0

# Lock down CORS to the real frontend origins (comma-separated)
CORS_ALLOWED_ORIGINS=https://zumud.com,https://www.zumud.com

# Set a permanent SECRET_KEY so JWTs survive restarts:
SECRET_KEY=<run `openssl rand -hex 32` and paste the result>

# Sentry (optional). If you set SENTRY_DSN, keep sample rates LOW in prod:
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

## 3. Free up disk and stop the log explosion

```bash
# See current log usage
du -sh log/

# Truncate noisy old logs (safe; the new code rotates+gzips going forward)
find log/ -type f -name 'app_*.log' -mtime +1 -delete
```

The new logger config:

- defaults to `INFO` (not DEBUG)
- silences `httpx`/`httpcore`/`hpack`/`urllib3`/`sqlalchemy.engine` to WARNING
- gzips rotated log files
- writes async (`enqueue=True`) so a slow disk can't stall request handling
- only includes local-variable diagnostics if you opt in with `LOG_DIAGNOSE=1`
  (this also stops sensitive values from being captured in tracebacks)

## 4. Run with multiple workers and auto-restart

### Option A — systemd (recommended)

```bash
# Adjust deploy/zumud-api.service: User, Group, WorkingDirectory
sudo cp deploy/zumud-api.service /etc/systemd/system/zumud-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now zumud-api

# Check it
sudo systemctl status zumud-api
journalctl -u zumud-api -f
```

systemd will:

- restart the service if it crashes (`Restart=always`, `RestartSec=3`)
- enforce a memory cap (`MemoryMax=80%`) so a runaway worker is killed before
  the VM OOMs the kernel and takes the whole host down
- aggregate logs into journald (so the app's own `log/` files stay smaller)

### Option B — quick fix without systemd

If you can't install systemd right now, at least run it under tmux + multi-worker:

```bash
tmux new -s zumud
./deploy/run-prod.sh
# Detach with Ctrl-B then D
```

uvicorn with `--workers 2` will respawn any worker that crashes. The master
still dies on signal, so you should still graduate to systemd.

## 5. Verify

```bash
# On the server, with the service running:
curl -s http://127.0.0.1:8000/health
# -> {"status":"healthy","database":"connected","version":"1.0.0"}

# From your laptop:
curl -sI https://api.zumud.com/health
# -> HTTP/2 200
```

If `127.0.0.1:8000/health` works on the server but `api.zumud.com/health`
returns 521, the problem is between Cloudflare and your server, not the app.
Check:

- Is nginx (or whatever reverse-proxies port 443) running? `sudo systemctl status nginx`
- Is the firewall allowing 443? `sudo ufw status`
- Are the Cloudflare origin IPs allowed in any IP allowlist?

## 6. Watch for the next crash

If it still happens after this:

```bash
# Most recent crashes / restarts
journalctl -u zumud-api --since '1 hour ago' -p err

# What killed it (OOM?)
sudo dmesg -T | grep -i 'killed process'

# Disk
df -h
du -sh /opt/zumud/log /var/log

# Open file descriptors per worker
sudo lsof -p $(pgrep -f 'backend.main:app' | head -n1) | wc -l

# Active Postgres connections (Supabase)
# In Supabase dashboard: Database -> Connection Pooling
```

The two specific failure modes still worth checking once stability is back:

- **Supabase connection limit**: free tier allows ~60 direct connections. With
  `pool_size=10` + `max_overflow=20` * `WEB_CONCURRENCY=2` workers you can use
  up to 60. If you scale workers, switch the `DATABASE_URL` to the Supabase
  **pooler** URL (port 6543, `pgbouncer=true`) or you will exhaust connections
  and the app will fail to serve requests.
- **LaTeX compiler**: `LATEX_COMPILER_BASE_URL` defaults to
  `http://127.0.0.1:2700`. If `latex-online` isn't running, every PDF request
  hangs on a TCP connect timeout and ties up a worker. Make sure that container
  is also under a supervisor.
