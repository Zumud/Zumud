"""The built-in template registry.

Templates are Jinja2 programs, and until now nothing executed them: a template that
crashed on a resume with (say) no skills section would only be discovered by a user
mid-application. These tests render every registered built-in against every fixture
the same way production does — `escape_latex()` then `Template(...).render(...)`, as
in `ai_service.generate_structured_latex_resume_async`.
"""

import json
from pathlib import Path

import pytest
from jinja2 import Template

from backend.models import templates as templates_module
from backend.models.resume_models import StructuredResume
from backend.models.templates import TEMPLATES_DIR, Template_Details
from backend.utils.file_ops import escape_latex

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"
FIXTURE_NAMES = ["resume_kitchen_sink", "resume_minimal"]


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / f"{name}.json").read_text(encoding="utf-8"))


def render(template_source: str, resume: dict) -> str:
    """Render exactly as the generation path does."""
    return Template(template_source).render(escape_latex(resume))


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_fixture_is_a_valid_structured_resume(fixture_name):
    """The fixtures are the contract templates are written against, so they must
    stay in step with the model the AI is asked to produce."""
    StructuredResume.model_validate(load_fixture(fixture_name))


@pytest.mark.parametrize("template", list(Template_Details))
@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_builtin_renders_a_complete_document(template, fixture_name):
    rendered = render(
        Template_Details[template]["structure"], load_fixture(fixture_name)
    )

    assert "\\documentclass" in rendered
    assert "\\begin{document}" in rendered
    assert "\\end{document}" in rendered
    # An unrendered statement delimiter means a tag was emitted rather than executed.
    assert "{%" not in rendered


@pytest.mark.parametrize("template", list(Template_Details))
def test_builtin_binds_the_resume_data(template):
    """A template that ignores its input still compiles, so assert the data landed."""
    resume = load_fixture("resume_kitchen_sink")
    rendered = render(Template_Details[template]["structure"], resume)

    assert "Nakamura" in rendered
    assert "Kaizen Robotics" in rendered
    assert "Kubernetes" in rendered
    assert "University of Iceland" in rendered
    assert "traceroute-rs" in rendered
    assert "Engineering Excellence Award" in rendered
    assert "Bounded-Staleness Replication" in rendered


@pytest.mark.parametrize("template", list(Template_Details))
def test_builtin_omits_sections_the_resume_does_not_have(template):
    """The minimal fixture has only a name and one employer; absent sections must not
    leave a stranded heading behind."""
    rendered = render(
        Template_Details[template]["structure"], load_fixture("resume_minimal")
    )

    assert "Sam Reyes" in rendered
    assert "Acme Corp" in rendered
    for absent in ("Skills", "Education", "Projects", "Publications", "Awards"):
        assert f"section{{{absent}}}" not in rendered


@pytest.mark.parametrize("template", list(Template_Details))
def test_builtin_escapes_special_characters(template):
    """`escape_latex` runs before rendering, so a literal ampersand from the AI must
    never reach the compiler unescaped."""
    rendered = render(
        Template_Details[template]["structure"], load_fixture("resume_kitchen_sink")
    )

    assert "R\\&D" in rendered
    assert "100\\% coverage" in rendered
    assert "under\\_score" in rendered


def test_every_registered_template_has_a_source_file():
    for template, details in Template_Details.items():
        assert details["structure"].strip(), f"{template} loaded an empty source"
        assert details["compiler"] in {"pdflatex", "xelatex", "lualatex"}


def test_no_latex_lives_in_the_python_module():
    """The point of the registry: LaTeX belongs in reviewable .tex.jinja files."""
    source = Path(templates_module.__file__).read_text(encoding="utf-8")

    assert "\\documentclass" not in source
    assert "\\begin{document}" not in source
    assert list(TEMPLATES_DIR.glob("*.tex.jinja")), "no template files on disk"
