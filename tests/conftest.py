import os

# Hermetic defaults so backend modules import in the unit lane with no real
# environment. setdefault means real values (local Supabase stack, live keys)
# always win in the integration / real-AI lanes.
os.environ.setdefault("DATABASE_URL", "postgresql://zumud:zumud@127.0.0.1:1/zumud")
os.environ.setdefault("OPEN_AI_KEY", "sk-test-not-a-real-key")
