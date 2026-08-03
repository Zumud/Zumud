"""Registry of the built-in resume templates.

A template is a Jinja2 program that renders a `StructuredResume` into a LaTeX
document, so the LaTeX itself lives in `backend/templates/*.tex.jinja` where it can
be reviewed, diffed and tested. This module only names each built-in and records the
compiler it needs; it deliberately contains no LaTeX.

Which template a user's resumes render with is a single slug stored on
`tailoring_options.resume_template`, in one of two forms:

    builtin:<slug>   one of BUILTINS below, backed by backend/templates/<slug>.tex.jinja
    user:<id>        one of the user's own rows in user_templates

Adding a built-in is therefore dropping a file in that directory and naming it here:
no migration, because the column is a plain string rather than a Postgres enum.
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

BUILTIN_PREFIX = "builtin:"
USER_PREFIX = "user:"

# Display name, one line for the gallery, and the latex-online command that compiles
# it. The Jinja2/LaTeX source is the matching backend/templates/<slug>.tex.jinja, and
# the gallery thumbnail is frontend/public/templates/<slug>.png — page one of the
# template rendered with backend/fixtures/resume_preview.json.
BUILTINS = {
    "mteck": {
        "name": "MTeck",
        "description": "Dense single column that fits a lot without feeling crowded.",
        "compiler": "pdflatex",
    },
}

DEFAULT_BUILTIN_SLUG = "mteck"
DEFAULT_TEMPLATE = f"{BUILTIN_PREFIX}{DEFAULT_BUILTIN_SLUG}"

# Converting an upload into a template takes a model several attempts and a real
# compile each time, far longer than a request should wait, so the row is created
# before its template exists. Only READY rows have `latex_content` and may be
# selected or rendered; FAILED rows are kept so the user is told why.
PENDING = "pending"
READY = "ready"
FAILED = "failed"


def load_template_source(slug: str) -> str:
    """Read a built-in template's Jinja2/LaTeX source from disk."""
    return (TEMPLATES_DIR / f"{slug}.tex.jinja").read_text(encoding="utf-8")


# Read eagerly so a missing or unreadable template file fails at import rather than
# on a user's first generation.
_SOURCES = {slug: load_template_source(slug) for slug in BUILTINS}


def builtin_template(slug: str) -> dict | None:
    """The renderable form of a built-in, or None if there is no such built-in."""
    spec = BUILTINS.get(slug)
    if spec is None:
        return None
    return {"structure": _SOURCES[slug], "compiler": spec["compiler"]}
