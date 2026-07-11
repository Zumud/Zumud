"""Live-model contract tests (the `real_ai` lane).

Run in the merge queue, nightly, and on PRs labeled `real-ai` — never on fork
PRs (no secrets there). Assertions are structural, not exact-text, because
model output varies; the CI step passes --reruns 1 to absorb provider hiccups.
"""

import os

import pytest

pytestmark = pytest.mark.real_ai

SMALL_RESUME = """Jane Doe
Senior Platform Engineer, Berlin
Experience: Acme Corp (2019-2026) - built Python delivery pipelines, led five engineers.
Education: BSc Computer Science, TU Berlin (2016).
Skills: Python, TypeScript, PostgreSQL, Docker.
"""

SMALL_JD = """Acme Robotics is hiring a Senior Python Engineer in Berlin to build
reliable backend services. Requirements: 5+ years Python, PostgreSQL, CI/CD.
"""


@pytest.fixture(autouse=True, scope="module")
def require_live_key():
    key = os.environ.get("OPEN_AI_KEY", "")
    if not key or "not-a-real-key" in key or key.startswith("ci-dummy"):
        pytest.skip("real_ai lane requires a live OPEN_AI_KEY")


def test_tailored_resume_text_contract():
    from backend.core.ai_service import generate_tailored_resume_text

    out = generate_tailored_resume_text(resume=SMALL_RESUME, job_description=SMALL_JD)
    assert isinstance(out, str)
    assert len(out) > 200, "tailored resume should be substantive"
    assert "jane" in out.lower(), "candidate identity must survive tailoring"


def test_company_name_extraction_contract():
    from backend.core.ai_service import get_company_name

    name = get_company_name(SMALL_JD)
    assert name and "acme" in name.lower()
