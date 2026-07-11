#!/usr/bin/env bash
# One-time GitHub repo configuration for the autonomous pipeline.
# Run AFTER the pipeline PR is merged (required-check names must exist).
# Requires: gh CLI authenticated with admin on Zumud/Zumud.
#
# Manual steps this script cannot do (dashboard-only):
#   1. Add the OPEN_AI_KEY actions secret:  gh secret set OPEN_AI_KEY
#   2. Install Cursor Bugbot on the repo (cursor.com/dashboard -> Bugbot).
#   3. Enable OpenAI Codex code review on the repo (chatgpt.com/codex).
#   4. After the first latex-image push: make the GHCR package
#      ghcr.io/zumud/zumud-latex PUBLIC (org -> Packages -> settings) so CI
#      and fork PRs can pull it anonymously.
#   5. External uptime monitor on https://api.zumud.com/health (UptimeRobot
#      or healthchecks.io free tier).
set -euo pipefail

REPO="Zumud/Zumud"

echo ">> repo merge settings (squash-only, auto-merge, tidy branches)"
gh api -X PATCH "repos/$REPO" \
  -F allow_auto_merge=true \
  -F delete_branch_on_merge=true \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false >/dev/null

echo ">> labels"
gh label create "tier:T2" --repo "$REPO" --color B60205 \
  --description "Sensitive change: needs the maintainer's approval to merge" --force
gh label create "scope-ok" --repo "$REPO" --color 0E8A16 \
  --description "Maintainer override: skip the scope gate" --force
gh label create "real-ai" --repo "$REPO" --color 5319E7 \
  --description "Run the live-model lane on this PR" --force
gh label create "agent-ok" --repo "$REPO" --color 1D76DB \
  --description "Spec is complete enough for autonomous implementation" --force
gh label create "flaky-quarantine" --repo "$REPO" --color FBCA04 \
  --description "Test quarantined as flaky; needs a fix issue" --force
gh label create "coverage-exempt" --repo "$REPO" --color 0E8A16 \
  --description "Skip the diff-coverage ratchet (mechanical bulk diffs only)" --force
gh label create "t2-approved" --repo "$REPO" --color 0E8A16 \
  --description "Maintainer sign-off on a tier:T2 PR (label appliers need triage+)" --force

echo ">> branch ruleset: protection + required checks + merge queue"
# Deletes a pre-existing ruleset of the same name so the script is rerunnable.
existing=$(gh api "repos/$REPO/rulesets" --jq \
  '.[] | select(.name == "main: gates + merge queue") | .id' || true)
if [ -n "$existing" ]; then
  gh api -X DELETE "repos/$REPO/rulesets/$existing" >/dev/null
fi

gh api -X POST "repos/$REPO/rulesets" --input - <<'JSON' >/dev/null
{
  "name": "main: gates + merge queue",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": false,
        "required_status_checks": [
          { "context": "Backend lint + unit tests" },
          { "context": "Integration tests (real Supabase stack)" },
          { "context": "Frontend lint + types + build" },
          { "context": "E2E smoke (mocked AI, real LaTeX)" },
          { "context": "Secret scan" },
          { "context": "Real-AI lane (live model, no mocks)" },
          { "context": "Scope coherence" },
          { "context": "T2 approval" }
        ]
      }
    },
    {
      "type": "merge_queue",
      "parameters": {
        "merge_method": "SQUASH",
        "grouping_strategy": "ALLGREEN",
        "max_entries_to_build": 5,
        "min_entries_to_merge": 1,
        "max_entries_to_merge": 5,
        "min_entries_to_merge_wait_minutes": 5,
        "check_response_timeout_minutes": 60
      }
    }
  ]
}
JSON

echo ">> done. Reminder of the manual steps in the header of this script."
