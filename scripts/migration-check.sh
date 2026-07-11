#!/usr/bin/env bash
# Prove the migration chain fully expresses the models:
#   1. upgrade head on a fresh scratch database
#   2. `alembic check` — fails if autogenerate would still emit anything
# Used by CI (integration job) and runnable locally against the Supabase
# stack's postgres. Never touches app databases.
set -euo pipefail
cd "$(dirname "$0")/.."

ADMIN_URL="${SCRATCH_ADMIN_URL:-postgresql://postgres:postgres@127.0.0.1:54322/postgres}"
SCRATCH_DB="alembic_drift_check"

PY=".venv/bin/python"; [ -x "$PY" ] || PY="python"
AL=".venv/bin/alembic"; [ -x "$AL" ] || AL="alembic"

"$PY" - "$ADMIN_URL" "$SCRATCH_DB" <<'EOF'
import sys
import sqlalchemy as sa

admin_url, scratch = sys.argv[1], sys.argv[2]
engine = sa.create_engine(admin_url, isolation_level="AUTOCOMMIT")
with engine.connect() as conn:
    conn.execute(sa.text(f'DROP DATABASE IF EXISTS "{scratch}"'))
    conn.execute(sa.text(f'CREATE DATABASE "{scratch}"'))
print(f"scratch database {scratch} ready")
EOF

SCRATCH_URL="${ADMIN_URL%/*}/${SCRATCH_DB}"
DATABASE_URL="$SCRATCH_URL" "$AL" upgrade head
DATABASE_URL="$SCRATCH_URL" "$AL" check
echo "OK: migrations fully express the models (no drift)"
