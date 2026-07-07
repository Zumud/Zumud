SHELL := /bin/bash
.DEFAULT_GOAL := help

# Local development against the Supabase CLI stack (Postgres + Auth + Storage + Mailpit).
# Requires Docker + the Supabase CLI. The backend's app tables are created by
# SQLAlchemy create_all() on first connect; the local DB schema therefore matches prod.

.PHONY: help up down reset status dev-backend dev-frontend seed latex-up latex-down latex-tunnel

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

up: ## Start the local Supabase stack
	set -a; [ -f supabase/.env.local ] && . supabase/.env.local; set +a; supabase start

down: ## Stop the local Supabase stack
	supabase stop

reset: ## Wipe + recreate the local database (re-runs create_all on next backend start)
	supabase db reset

status: ## Show local stack URLs/keys
	supabase status

# Pull local creds from `supabase status` and map them onto the backend's env names,
# then run uvicorn. python-dotenv (load_dotenv) does NOT override real env vars, so these
# exported local values win over the committed cloud .env.
dev-backend: ## Run the FastAPI backend against the local stack
	set -a; \
	eval "$$(supabase status -o env 2>/dev/null | grep -E '^[A-Z0-9_]+=')"; \
	if [ -z "$$DB_URL" ]; then \
	  echo "ERROR: couldn't read local Supabase creds (DATABASE_URL would be empty)."; \
	  echo "  - Run 'make up' first if the stack isn't running."; \
	  echo "  - Docker must be reachable from this shell ('docker ps' must work). On snap-Docker/WSL"; \
	  echo "    the 'docker' group needs a fresh login: run 'newgrp docker' (or restart WSL), or use:"; \
	  echo "    sg docker -c 'make dev-backend'"; \
	  exit 1; \
	fi; \
	export SUPABASE_URL="$$API_URL" \
	       SUPABASE_PUBLISHABLE_KEY="$$PUBLISHABLE_KEY" \
	       SUPABASE_SECRET_KEY="$$SECRET_KEY" \
	       SUPABASE_JWT_SECRET="$$JWT_SECRET" \
	       DATABASE_URL="$$DB_URL" \
	       LATEX_COMPILER_BASE_URL="http://127.0.0.1:2700" \
	       ENVIRONMENT="development"; \
	set +a; \
	.venv/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend: ## Run the Next.js frontend against the local stack (uses frontend/.env.local)
	cd frontend && npm run dev

seed: ## Create a confirmed local test user ([email protected] / password123)
	@eval "$$(supabase status -o env 2>/dev/null | grep -E '^[A-Z0-9_]+=')"; \
	curl -s -X POST "$$API_URL/auth/v1/admin/users" \
	  -H "apikey: $$SERVICE_ROLE_KEY" -H "Authorization: Bearer $$SERVICE_ROLE_KEY" \
	  -H "Content-Type: application/json" \
	  -d '{"email":"[email protected]","password":"password123","email_confirm":true}' >/dev/null \
	  && echo "seeded: [email protected] / password123" || echo "seed failed"

# Local LaTeX compiler (PDF generation). Same image as prod: TeX Live 2024 +
# latex-online served on 127.0.0.1:2700. First `latex-up` builds the image
# (~4-5GB base pull); the first compile lags ~30s while the entrypoint clones
# latex-online. The backend defaults LATEX_COMPILER_BASE_URL to this address.
latex-up: ## Build (first run) + start the local LaTeX compiler on 127.0.0.1:2700
	docker image inspect zumud-latex:modern >/dev/null 2>&1 || docker build -t zumud-latex:modern docker/latex
	docker rm -f zumud-latex >/dev/null 2>&1 || true
	docker run -d --name zumud-latex --restart unless-stopped -p 2700:2700 zumud-latex:modern
	@echo "LaTeX compiler on http://127.0.0.1:2700 (first request lags ~30s while it clones latex-online)"

# Note: published on 0.0.0.0:2700 (not 127.0.0.1) because snap-Docker's loopback port
# proxy doesn't forward to containers under WSL; 0.0.0.0 is reachable via 127.0.0.1 from
# the host. Prod publishes 127.0.0.1:2700 (real Docker forwards loopback fine).

latex-down: ## Stop + remove the local LaTeX compiler
	docker rm -f zumud-latex >/dev/null 2>&1 || true

# Alternative to latex-up: tunnel local :2700 to a remote latex-online container.
# Provide the SSH target/options via LATEX_SSH (kept out of the repo), e.g.:
#   make latex-tunnel LATEX_SSH="-i ~/.ssh/id_ed25519 root@<host>"
latex-tunnel: ## SSH-tunnel local :2700 to a remote latex container (set LATEX_SSH=...)
	ssh -N -L 127.0.0.1:2700:127.0.0.1:2700 $(LATEX_SSH)
