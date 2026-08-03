"""Registry of the built-in resume templates.

A template is a Jinja2 program that renders a `StructuredResume` into a LaTeX
document, so the LaTeX itself lives in `backend/templates/*.tex.jinja` where it can
be reviewed, diffed and tested. This module only names each built-in and records the
compiler it needs; it deliberately contains no LaTeX.
"""

from enum import Enum
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"


class ResumeTemplate(str, Enum):
    MTeck_resume = "MTeck's Resume"


# Which file backs each template, and which latex-online command compiles it.
_BUILTINS = {
    ResumeTemplate.MTeck_resume: {"slug": "mteck", "compiler": "pdflatex"},
}


def load_template_source(slug: str) -> str:
    """Read a built-in template's Jinja2/LaTeX source from disk."""
    return (TEMPLATES_DIR / f"{slug}.tex.jinja").read_text(encoding="utf-8")


# Read eagerly so a missing or unreadable template file fails at import rather than
# on a user's first generation.
Template_Details = {
    template: {
        "structure": load_template_source(spec["slug"]),
        "compiler": spec["compiler"],
    }
    for template, spec in _BUILTINS.items()
}
