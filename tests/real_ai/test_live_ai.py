"""Live-model contract tests (the `real_ai` lane).

Run in the merge queue, nightly, and on PRs labeled `real-ai` — never on fork
PRs (no secrets there). Assertions are structural, not exact-text, because
model output varies; the CI step passes --reruns 1 to absorb provider hiccups.
"""

import asyncio
import json
import os
from types import SimpleNamespace

import pytest

from backend.utils.writing_quality import find_writing_quality_issues

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


def test_tailored_coverletter_text_contract():
    from backend.core.ai_service import generate_tailored_coverletter_text

    out = generate_tailored_coverletter_text(
        resume=SMALL_RESUME, job_description=SMALL_JD
    )
    assert isinstance(out, str)
    assert len(out) > 200, "tailored cover letter should be substantive"
    assert "acme" in out.lower(), "cover letter should address the company"
    assert find_writing_quality_issues(out) == []


def test_application_answer_text_contract():
    from backend.core.ai_service import generate_answer_questions

    out = generate_answer_questions(
        resume=SMALL_RESUME,
        job_description=SMALL_JD,
        question="What experience prepares you to build our backend services?",
    )

    assert isinstance(out, str)
    assert "python" in out.lower()
    assert find_writing_quality_issues(out) == []


def test_tailored_resume_text_contract(monkeypatch, tmp_path):
    from backend.core import ai_service

    monkeypatch.setattr(
        ai_service,
        "generate_pdf_from_latex",
        lambda *_args, **_kwargs: SimpleNamespace(content=b"%PDF"),
    )
    _, _, content = asyncio.run(
        ai_service.generate_structured_latex_resume_async(
            save_folder=str(tmp_path),
            resume=SMALL_RESUME,
            job_description=SMALL_JD,
        )
    )
    resume = json.loads(content)

    assert resume["personal_info"]["name"] == "Jane Doe"
    assert "python" in content.lower()
    assert find_writing_quality_issues(content) == []


def test_company_name_extraction_contract():
    from backend.core.ai_service import get_company_name

    name = get_company_name(SMALL_JD)
    assert name and "acme" in name.lower()
