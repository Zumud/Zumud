# Dev pipeline — how changes reach production

The repo is built for high-throughput, largely autonomous development: agents
(and humans) open PRs, machine gates verify them, clean PRs merge themselves
through the merge queue, and the VPS deploys `main` on a 10-minute pull loop
with health-checked rollback ([deploy/README.md](../deploy/README.md)).

## Test lanes

| Lane | What's real | Trigger | Command |
|---|---|---|---|
| Unit | nothing external — no DB, network, secrets | every PR (fork-safe) | `make test` |
| Integration | Supabase stack (Postgres + GoTrue), full API | every PR | `make test-integration` |
| E2E smoke | everything incl. LaTeX compiler; AI stubbed deterministically | every PR | `./scripts/e2e-stack.sh` |
| Real-AI | everything incl. the live model — no mocks at all | merge queue, nightly, `real-ai` label | `pytest -m real_ai` + `E2E_REAL_AI=1 ./scripts/e2e-stack.sh` |

Nothing lands on `main` without passing a genuine model call and a real LaTeX
compile (the merge queue runs the real-AI lane). Fork PRs never receive
secrets; their real-AI run happens in the queue after maintainer approval.

## Gates (all required checks)

- **Correctness**: ruff (+format), tsc, eslint, pytest lanes, Playwright.
- **Structure**: import-linter layering (`api -> core -> utils -> models ->
  config`), knip (dead files/exports/deps; `src/components/ui/**` shadcn kit
  exempt), diff-coverage ratchet (changed lines need 80%; no absolute-%
  theater), Alembic drift check (model change without migration fails).
- **Security**: gitleaks, pip-audit, npm audit, CodeQL.
- **Scope coherence** (`scripts/scope_gate.py`): judges one-purpose,
  diff-vs-description proportionality, unrequested abstractions, duplication,
  and dependency justification against
  [.cursor/rules/principles.mdc](../.cursor/rules/principles.mdc). There are
  deliberately **no line-count limits**. Override label: `scope-ok`.
- **AI reviewers**: Bugbot + Codex review (different model family than the
  authoring agents). Findings block auto-merge until fixed or explicitly
  rebutted; configured bugs-only — linters own style.

## Risk tiers (merge policy)

- **T0/T1** (default): green checks + clean AI review → **auto-merge** via the
  merge queue. Enable auto-merge on the PR; no human involved.
- **T2** (auto-labeled `tier:T2` — dependencies, auth, billing, migrations,
  `.github/`, `deploy/`, `scripts/`): everything above **plus** the
  maintainer's PR approval (enforced by the "T2 approval" check). All
  external/fork PRs are effectively T2: first-time contributors also need
  workflow-run approval, and bot verdicts on fork PRs are advisory only
  (prompt-injection caution).

## Working conventions

- One purpose per PR; the PR body states what/why/verification (template).
- Specs live as issues (template: "Spec (agent-ready task)"); `agent-ok`
  means specified well enough for an agent to pick up autonomously.
- Behavior changes need tests in the right lane — diff coverage enforces it.
- Migrations: expand/contract (add nullable → backfill → contract in a later
  PR). Migrations are always T2.
- Flaky test = pipeline outage at high merge volume. Quarantine immediately
  (skip + `flaky-quarantine` label + an issue), fix async.
- Schema changes: `alembic revision --autogenerate -m "..."` against the
  local stack, then `./scripts/migration-check.sh`.

## Repo configuration

Branch protection, merge queue, labels, and merge settings are codified in
[scripts/setup-repo.sh](../scripts/setup-repo.sh) (run once after this lands;
its header lists the dashboard-only steps: `OPEN_AI_KEY` secret, Bugbot,
Codex review, GHCR package visibility, uptime monitor).
