"""The e2e AI stub has to answer a templatization request with a real template.

The templatizer accepts nothing it has not rendered against both reference resumes,
so a stub whose guarding slips stops standing in for the model and starts testing the
failure path — and the e2e lane would report that as an upload the user cannot use.
Compiling needs the LaTeX service, which this lane does not have; rendering is the
half that breaks silently, so it is the half checked here.
"""

import re

import pytest

from backend.core.templatizer import missing_sections
from backend.fixtures import VERIFICATION_RESUMES, load_resume
from backend.utils.file_ops import escape_latex
from backend.utils.jinja_env import render_resume_template
from tests.e2e.mock_openai import TEMPLATIZED_BODY, _is_templatization

# An environment opened with no \item in it is a compile error, which is exactly what
# an unguarded loop over an absent list produces.
EMPTY_ENVIRONMENT = re.compile(r"\\begin\{itemize\}\s*\\end\{itemize\}")


@pytest.fixture(params=VERIFICATION_RESUMES)
def rendered(request):
    return render_resume_template(
        TEMPLATIZED_BODY, escape_latex(load_resume(request.param))
    )


def test_it_renders_the_candidates_name(rendered):
    """The one field every resume has, and the check verify() makes first."""
    names = [
        escape_latex(load_resume(name))["personal_info"]["name"]
        for name in VERIFICATION_RESUMES
    ]

    assert any(name in rendered for name in names)


def test_it_opens_no_empty_lists(rendered):
    assert not EMPTY_ENVIRONMENT.search(rendered)


def test_it_strands_no_headings():
    """A resume with nothing but a name and an employer gets Experience and no more."""
    rendered = render_resume_template(
        TEMPLATIZED_BODY, escape_latex(load_resume("resume_minimal"))
    )

    assert "Experience" in rendered
    assert "Skills" not in rendered
    assert "Education" not in rendered


def test_it_leaves_the_gaps_the_fill_is_for():
    """Deliberately not a complete template.

    The stub answers the way a model does — with the design in front of it, printing what
    that design printed — so the sections it omits are what the e2e lane then watches
    fill_missing_sections supply. A stub that covered everything would quietly stop
    testing that.
    """
    name = "resume_kitchen_sink"
    escaped = escape_latex(load_resume(name))

    assert missing_sections(name, escaped, TEMPLATIZED_BODY)


def test_only_the_templatizer_gets_a_template():
    """Tailoring calls are plain completions too, and must keep their own fixture."""
    templatizing = {
        "messages": [
            {"role": "system", "content": "You convert LaTeX resumes into Jinja2..."},
            {"role": "user", "content": "Convert this body"},
        ]
    }
    tailoring = {"messages": [{"role": "user", "content": "Tailor this resume"}]}

    assert _is_templatization(templatizing)
    assert not _is_templatization(tailoring)
    assert not _is_templatization({})
