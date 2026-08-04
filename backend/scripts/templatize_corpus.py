"""How well does the templatizer cope with the resumes people actually have?

"Upload your own LaTeX" is only worth offering if it works on real documents, and the
only honest way to know is to run real ones through it. This fetches well-known
open-source resume templates, converts each one, and reports what happened — which is
both a measure of the feature and the way we find designs worth shipping ourselves.

A conversion costs several model calls and a real compile each time, so this is a
manual tool rather than a CI lane. It needs a real OPEN_AI_KEY and the LaTeX compiler
(`make latex-up`). Run from the repo root:

    .venv/bin/python -m backend.scripts.templatize_corpus
    .venv/bin/python -m backend.scripts.templatize_corpus --out /tmp/corpus jake

Sources are fetched rather than vendored: we redistribute our own derived templates,
not other people's documents, and each one we adopt gets its licence and author
recorded in the header of the template it became (see backend/templates/mteck.tex.jinja).

Deliberately absent are the famous ones that ship a class file — Awesome-CV, AltaCV,
Deedy, simple-resume-cv. A `.tex` that says \\documentclass{altacv} is not a document
anyone can upload, because the class is not in TeX Live and we take a single file. That
they are excluded is itself a result: those designs can only reach users as built-ins,
with the class inlined into the preamble the way mteck's is.
"""

import argparse
import sys
import time
import urllib.request
from pathlib import Path

from backend.core.templatizer import TemplatizationError, templatize

# Real documents, each a single .tex that compiles against TeX Live as it stands —
# the same thing an upload has to be.
CORPUS = {
    "jake": {
        "name": "Jake's Resume",
        "author": "Jake Gutierrez",
        "license": "MIT",
        "url": "https://raw.githubusercontent.com/jakegut/resume/master/resume.tex",
    },
    "sb2nov": {
        "name": "Sourabh Bajaj's Resume",
        "author": "Sourabh Bajaj",
        "license": "MIT",
        "url": "https://raw.githubusercontent.com/sb2nov/resume/master/sourabh_bajaj_resume.tex",
    },
    "moderncv": {
        "name": "moderncv (classic)",
        "author": "Xavier Danaux",
        "license": "LPPL-1.3c",
        "url": "https://raw.githubusercontent.com/xdanaux/moderncv/master/examples/template.tex",
        # Expected to fail: moderncv builds its page footer from \name at
        # \begin{document}, so the declaration cannot be moved into the body where the
        # model is allowed to rewrite it. See relocate_personal_data.
    },
    "latexcv": {
        "name": "latexcv (classic)",
        "author": "Jan Küster",
        "license": "MIT",
        "url": "https://raw.githubusercontent.com/jankapunkt/latexcv/master/classic/main.tex",
    },
}

CACHE = Path("/tmp/zumud-corpus")


def emit(line: str) -> None:
    """Report a line to the terminal, once.

    Importing anything under `backend/` routes stdout through loguru, which would echo
    the report as a log line as well. The report is this script's output, not logging.
    """
    print(line, file=sys.__stdout__)


def fetch(slug: str, url: str) -> str:
    """The document, from cache if it is already here — prompts get iterated on."""
    cached = CACHE / f"{slug}.tex"
    if not cached.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=30) as response:
            cached.write_bytes(response.read())
    return cached.read_text(encoding="utf-8", errors="replace")


def convert(slug: str, out: Path) -> tuple[str, str]:
    """Convert one document. Returns (outcome, detail) — never raises."""
    spec = CORPUS[slug]
    try:
        source = fetch(slug, spec["url"])
    except Exception as exc:
        return "unreachable", f"{type(exc).__name__}: {exc}"

    started = time.monotonic()
    try:
        verified = templatize(source)
    except TemplatizationError as exc:
        (out / f"{slug}.error.txt").write_text(str(exc), encoding="utf-8")
        # The first line is the failure; the rest is the compiler's transcript.
        return "failed", str(exc).splitlines()[0]
    except Exception as exc:
        return "crashed", f"{type(exc).__name__}: {exc}"

    (out / f"{slug}.tex.jinja").write_text(verified.source, encoding="utf-8")
    return "converted", f"{verified.compiler}, {time.monotonic() - started:.0f}s"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "slugs",
        nargs="*",
        default=sorted(CORPUS),
        help="documents to convert; defaults to the whole corpus",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("/tmp/zumud-corpus-out"),
        help="where to write the templates that worked, for a human to judge",
    )
    # The model is asked three times per conversion and a document that converts on one
    # run can fail the next, so a single pass is an anecdote rather than a rate.
    parser.add_argument(
        "--runs", type=int, default=1, help="conversions per document (default 1)"
    )
    args = parser.parse_args()

    unknown = [slug for slug in args.slugs if slug not in CORPUS]
    if unknown:
        print(f"not in the corpus: {', '.join(unknown)}", file=sys.stderr)
        return 2

    args.out.mkdir(parents=True, exist_ok=True)
    results = {
        slug: [convert(slug, args.out) for _ in range(args.runs)] for slug in args.slugs
    }

    emit(f"\n{'source':<10} {'licence':<10} result")
    worked = 0
    for slug, runs in results.items():
        wins = [detail for outcome, detail in runs if outcome == "converted"]
        worked += bool(wins)
        # The detail of a win is the engine and how long the user would have waited; of
        # a loss, what to fix. Either way the first one is enough to act on.
        detail = wins[0] if wins else runs[0][1]
        emit(
            f"{slug:<10} {CORPUS[slug]['license']:<10} "
            f"{len(wins)}/{args.runs} converted — {detail}"
        )

    emit(f"\n{worked}/{len(results)} documents converted, written to {args.out}")
    # Nothing at all working means the tool is broken, not the corpus: no key, no
    # compiler, a prompt that stopped producing LaTeX.
    return 0 if worked else 1


if __name__ == "__main__":
    raise SystemExit(main())
