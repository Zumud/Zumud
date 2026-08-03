"""Reference resumes that every template must survive.

These are the data contract: `resume_kitchen_sink` populates every optional
section and includes unicode and LaTeX special characters, `resume_minimal`
supplies nothing but a name and one employer. A template that renders both and
compiles is a template we are willing to hand a user.

They live under `backend/` rather than `tests/` because the templatizer verifies
generated templates against them at runtime, not only in the test suite.
"""

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent

KITCHEN_SINK = "resume_kitchen_sink"
MINIMAL = "resume_minimal"
VERIFICATION_RESUMES = (KITCHEN_SINK, MINIMAL)


def load_resume(name: str) -> dict:
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))
