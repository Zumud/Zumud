"""Render the gallery thumbnail for each built-in template.

The gallery shows what a template looks like, and the honest way to produce that is
to render the real template with a real resume and photograph page one. The results
are committed under frontend/public/templates/ so the profile page costs no compile,
and regenerating them is this script rather than a memory of how it was done.

Needs the LaTeX compiler running (`make latex-up`). Run from the repo root:

    .venv/bin/python -m backend.scripts.render_template_previews
"""

import argparse
import sys
import tempfile
from pathlib import Path

import pypdfium2

from backend.fixtures import PREVIEW, load_resume
from backend.models.templates import BUILTINS, builtin_template
from backend.utils.file_ops import escape_latex, generate_pdf_from_latex
from backend.utils.jinja_env import render_resume_template

PREVIEW_DIR = Path(__file__).resolve().parents[2] / "frontend/public/templates"

# Wide enough to stay sharp on a retina display at the size the gallery draws it.
PREVIEW_WIDTH = 600


def render(slug: str, resume: dict) -> bytes:
    """Page one of a built-in template, as a PNG."""
    template = builtin_template(slug)
    latex = render_resume_template(template["structure"], escape_latex(resume))

    with tempfile.TemporaryDirectory() as tmp:
        response = generate_pdf_from_latex(tmp, latex, template["compiler"])

    page = pypdfium2.PdfDocument(response.content)[0]
    image = page.render(scale=PREVIEW_WIDTH / page.get_width()).to_pil()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "page.png"
        image.save(out, format="PNG", optimize=True)
        return out.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "slugs",
        nargs="*",
        default=sorted(BUILTINS),
        help="built-ins to render; defaults to all of them",
    )
    args = parser.parse_args()

    resume = load_resume(PREVIEW)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    for slug in args.slugs:
        if slug not in BUILTINS:
            print(f"{slug}: not a built-in template", file=sys.stderr)
            return 1
        destination = PREVIEW_DIR / f"{slug}.png"
        destination.write_bytes(render(slug, resume))
        print(f"{slug} -> {destination.relative_to(PREVIEW_DIR.parents[2])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
