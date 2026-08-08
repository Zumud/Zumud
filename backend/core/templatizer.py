"""Turning a user's LaTeX resume into a template we can render anyone's data into.

The hard part is that the output has to be a working Jinja2 program, not merely
plausible LaTeX, and a model asked to rewrite a whole document will happily reword a
package option or drop a macro definition and produce something that no longer
compiles. Two things keep that in check:

*Freeze the preamble.* Everything up to `\\begin{document}` is passed to the model as
read-only context — so it knows which macros the document defines — and then our copy
is reattached verbatim. The model only ever authors the body, so it cannot break the
document's setup even if it tries. The exception is personal data: some classes
declare the candidate in the preamble, and freezing that would nail the original
author's name into every resume the template produces, so those declarations are
moved into the body first (see `relocate_personal_data`).

*Verify before accepting.* A candidate is rendered against both reference resumes and
actually compiled. Anything that fails — a syntax error, an unrendered tag, a
compiler error, or a template that quietly ignores the data it was given — goes back
to the model as feedback, up to MAX_ATTEMPTS times. Nothing is stored until it has
produced a real PDF from both fixtures.
"""

import re
import tempfile
from typing import NamedTuple

from openai import OpenAI

from backend.config.envs import OPEN_AI_KEY
from backend.fixtures import VERIFICATION_RESUMES, load_resume
from backend.models.ai_models import AIModel
from backend.models.resume_models import StructuredResume
from backend.models.templates import builtin_template, load_template_source
from backend.utils.file_ops import escape_latex, generate_pdf_from_latex
from backend.utils.jinja_env import render_resume_template
from backend.utils.log import logger

MAX_ATTEMPTS = 3

# Tried in order. pdflatex first because it is much faster and most designs build
# under it; xelatex is what fontspec/unicode-math preambles need. Both engines work
# everywhere now — docker/latex/ builds xelatex.fmt into the image, and the deploy
# host refuses an image that cannot compile fontspec (deploy/zumud-deploy.sh).
COMPILERS = ("pdflatex", "xelatex")

# Templatizing is a harder, rarer task than tailoring, so it does not follow the
# user's chosen tailoring model.
TEMPLATIZER_MODEL = AIModel.gpt_4_1_mini

BEGIN_DOCUMENT = re.compile(r"\\begin\s*\{document\}")
END_DOCUMENT = re.compile(r"\\end\s*\{document\}")

client = OpenAI(api_key=OPEN_AI_KEY)


class TemplatizationError(Exception):
    """A user's .tex could not be turned into a template that renders and compiles."""


class VerifiedTemplate(NamedTuple):
    """A template that has rendered and compiled, with the engine that built it."""

    source: str
    compiler: str


def split_document(source_tex: str) -> tuple[str, str]:
    """Split into (preamble through \\begin{document}, body before \\end{document})."""
    begin = BEGIN_DOCUMENT.search(source_tex)
    if begin is None:
        raise TemplatizationError(
            "No \\begin{document} found — this does not look like a complete LaTeX document."
        )

    end = END_DOCUMENT.search(source_tex, begin.end())
    if end is None:
        raise TemplatizationError("No \\end{document} found after \\begin{document}.")

    return source_tex[: begin.end()], source_tex[begin.end() : end.start()]


# Commands that carry the candidate rather than the design. altacv and friends put
# these in the preamble and only call the header macro in the body, so a frozen
# preamble would keep the original owner's name and email on every resume rendered
# from the template — which verification then rejects, failing a usable upload.
#
# Known limit: a class that consumes the value at \begin{document} rather than where
# the header is typeset cannot take the declaration from the body — moderncv's
# classic style builds its page footer from \name and fails with an undefined
# \@firstname. Supporting those needs the declarations templatized in place, in the
# preamble, rather than moved.
PERSONAL_COMMANDS = (
    "name",
    "born",
    "firstname",
    "familyname",
    "givenname",
    "address",
    "phone",
    "mobile",
    "email",
    "homepage",
    "website",
    "social",
    "photo",
    "extrainfo",
    "tagline",
    "personalinfo",
    "position",
    "quote",
    "title",
    "author",
    "date",
)

_PERSONAL_DECLARATION = re.compile(
    r"^[ \t]*\\(?:" + "|".join(PERSONAL_COMMANDS) + r")(?![a-zA-Z@])", re.MULTILINE
)


def _group_end(text: str, start: int) -> int | None:
    """Index just past the group opening at `start`, or None if it never closes."""
    closing = {"{": "}", "[": "]"}[text[start]]
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\":  # an escaped brace delimits nothing
            index += 2
            continue
        if char == text[start]:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _declaration_end(text: str, start: int) -> int:
    """Index just past the argument list of a command whose name ends at `start`."""
    index = start
    while index < len(text) and text[index] in " \t":
        index += 1
    while index < len(text) and text[index] in "{[":
        end = _group_end(text, index)
        if end is None:
            return index
        index = end
        while index < len(text) and text[index] in " \t":
            index += 1
    return index


def relocate_personal_data(preamble: str, body: str) -> tuple[str, str]:
    """Move the candidate's details out of the frozen preamble and into the body.

    LaTeX does not care where `\\name` is set so long as it precedes `\\makecvtitle`,
    so moving the declarations past `\\begin{document}` changes nothing about the
    output while putting them somewhere the model is allowed to rewrite.
    """
    kept: list[str] = []
    moved: list[str] = []
    cursor = 0

    for match in _PERSONAL_DECLARATION.finditer(preamble):
        if match.start() < cursor:
            continue
        end = _declaration_end(preamble, match.end())
        kept.append(preamble[cursor : match.start()])
        moved.append(preamble[match.start() : end].strip())
        cursor = end

    if not moved:
        return preamble, body

    kept.append(preamble[cursor:])
    return "".join(kept), "\n".join(moved) + "\n" + body


ENDRAW = re.compile(r"\{%-?\s*endraw\s*-?%\}")


def protect(preamble: str) -> str:
    """Mark the preamble as literal text rather than template source.

    A LaTeX macro definition writes its parameters as `{#1}`, and Jinja reads `{#`
    as the start of a comment — so a preamble containing `\\newcommand{\\x}[1]{#1}`
    makes the whole file unparseable before any field is ever substituted. The
    preamble is by definition not templated, so saying so is both the smallest fix
    and the honest one. (The built-in template predates this and works around the
    same collision by hand, writing `{{ '{#' }}` at each site.)

    An upload that itself contains `{% endraw %}` would close the block early and
    hand the remainder of its own preamble back to Jinja as template source, which
    is the one way a crafted .tex could get out of the freeze — so those tokens are
    emitted as data instead.
    """
    escaped = ENDRAW.sub(
        lambda token: f"{{% endraw %}}{{{{ {token.group()!r} }}}}{{% raw %}}", preamble
    )
    return f"{{% raw %}}{escaped}{{% endraw %}}"


RULES = r"""
You are converting the body of a LaTeX resume into a Jinja2 template. The template
will be rendered with one candidate's data and compiled, over and over, for many
different candidates.

The data you will receive at render time matches this JSON schema exactly:

%(schema)s

Rules, all of them mandatory:

1. Return ONLY the document body. Do not include the preamble, \begin{document} or
   \end{document}. Do not wrap the answer in markdown fences.
2. Replace every piece of the original candidate's hardcoded content with the
   corresponding field. Nothing personal from the original document may survive.
3. Every list field is variable length. Loop over it; never assume a count.
4. Every field except personal_info.name is optional. Guard each section so that a
   resume without it renders no heading, no rules, and no empty space — a stranded
   "Education" heading with nothing under it is a defect. Guard the inner lists too:
   a list environment opened with no \item in it is a compile error, so a job with
   no achievements must emit no list at all rather than an empty one.
5. The values are ALREADY LaTeX-escaped before rendering. Never add \textbackslash,
   \&, escaping filters, or |e. Use values as they are.
6. Use only macros that appear in the preamble or in the body you are converting,
   plus standard LaTeX. The worked example below is a DIFFERENT document: macros
   like \documentTitle and \headingBf are defined by its preamble and do not exist
   here. Copying one produces "Undefined control sequence". Take the guarding and
   looping from the example; take the macros from the document in front of you.
7. Keep every command the original body calls. Templatize its arguments, and guard
   it if the data may be absent — but do not drop it. A class that typesets its
   header from \name fails to compile if \name is gone.
8. Keep the original's visual design: same sections in the same order, same spacing
   and typography. You are changing where the content comes from, not how it looks.
9. Write the list of skills as skill['items'], never skill.items. Jinja resolves an
   attribute before a key, and `.items` finds Python's dictionary method instead of
   the field — which renders as a method object rather than the skills.
10. `{#` opens a comment in Jinja, so a LaTeX group starting with a macro parameter —
   `{#1}` — makes the file unparseable. Write such a group as `{{ '{#' }}1}`. Never
   open a Jinja comment yourself.
"""


def _rules() -> str:
    # The sections are named from the same place verification looks for them, so what the
    # model is told to produce cannot drift from what it is judged on.
    return RULES % {"schema": StructuredResume.model_json_schema()}


def _worked_example() -> str:
    """The one template known to render both fixtures and compile."""
    _, body = split_document(builtin_template("mteck")["structure"])
    return (
        "Here is a body that satisfies all of the above, for a different design and "
        "a different preamble. Match its guarding and looping; do not reuse its "
        "macros:\n\n"
        f"{body}"
    )


def build_prompt(preamble: str, body: str, feedback: str | None = None) -> str:
    sections = [
        _rules(),
        _worked_example(),
        (
            "This document's preamble is READ-ONLY context so you know which macros "
            f"are available. Do not reproduce or modify it:\n\n{preamble}"
        ),
        f"Convert this body:\n\n{body}",
    ]
    if feedback:
        sections.append(
            "Your previous attempt was rejected. Fix exactly this and return the "
            f"whole body again:\n\n{feedback}"
        )
    return "\n\n---\n\n".join(sections)


def _strip_fences(text: str) -> str:
    """Models wrap LaTeX in markdown fences despite being told not to."""
    fenced = re.match(r"\s*```(?:latex|tex)?\n(.*)\n```\s*\Z", text, re.DOTALL)
    return fenced.group(1) if fenced else text.strip()


def _compile_with_a_working_engine(renders: dict[str, str], compile_pdf) -> str:
    """The first engine that builds every render, or a TemplatizationError.

    Which engine a document needs is a property of its preamble, not something we
    are told: `fontspec` and `unicode-math` require xelatex, while plenty of
    designs only build under pdflatex. So try them in turn and report the one that
    worked, because that is what has to be stored alongside the template.

    Only the first engine's failure is reported. The feedback exists for the model
    to fix its own LaTeX, and it cannot change the frozen preamble that decides the
    engine — so the readable pdflatex error serves it better than a later engine
    complaining the format file is missing.
    """
    failure = ""
    for compiler in COMPILERS:
        for name, rendered in renders.items():
            with tempfile.TemporaryDirectory() as tmp:
                try:
                    compile_pdf(tmp, rendered, compiler)
                except ValueError as exc:
                    failure = failure or (
                        f"Compiling the '{name}' resume failed:\n{exc}"
                    )
                    break
        else:
            return compiler

    raise TemplatizationError(failure)


# The sections of a resume, every one of which a template has to print. Not a check that
# a section is complete — a check that it is there at all, which is the failure that
# hides: a design with no publications heading converts happily into a template that
# renders, carries the name and compiles, while quietly discarding the publications of
# everyone who uses it.
SECTIONS = (
    "summary",
    "skills",
    "experience",
    "education",
    "certifications",
    "projects",
    "publications",
    "awards",
)


def _render(what: str, escaped: dict, template_source: str) -> str:
    """One resume through the candidate, failing the way the model is told.

    `what` names the resume as the model should hear it — the failure is fed straight
    back, so "without its education" is the difference between a fixable report and an
    unexplained TypeError.
    """
    try:
        return render_resume_template(template_source, escaped)
    except Exception as exc:
        # Not just TemplateError: a template is arbitrary code to Jinja, and a filter
        # applied to the wrong type raises straight out of the stdlib.
        raise TemplatizationError(
            f"Rendering {what} raised {type(exc).__name__}: {exc}"
        ) from exc


def missing_sections(name: str, escaped: dict, template_source: str) -> list[str]:
    """Sections of this resume that make no difference to what the template prints.

    Asked by taking each section away and rendering again, rather than by looking for
    the section's values in the output: the reference resume has an academic employer, so
    "University of Iceland" appears whether or not education is printed, and searching
    for it would pass a template that drops every degree its users have. Whether a
    template reads a section is a question only the template can answer.
    """
    printed = _render(f"the '{name}' resume", escaped, template_source)

    absent = []
    for section in SECTIONS:
        if not escaped.get(section):
            continue
        # None rather than [], because that is what a resume without the section holds —
        # and a template that raises on it is one no such candidate could use, which is
        # a rejection in its own right rather than something to work around here.
        without = _render(
            f"the '{name}' resume without its {section}",
            {**escaped, section: None},
            template_source,
        )
        if without == printed:
            absent.append(section)
    return absent


# The blocks we add for sections a design does not print, keyed by section. They live in
# backend/templates/fallback_sections.tex.jinja, one `% == <section> ==` marker apiece,
# so they can be read as the LaTeX they are. Read at import so a broken file fails on
# startup rather than on somebody's upload.
_MARKER = re.compile(r"^% == (\w+) ==$", re.MULTILINE)


def _fallback_sections() -> dict[str, str]:
    parts = _MARKER.split(load_template_source("fallback_sections"))
    # split() yields [text before the first marker, name, block, name, block, ...].
    blocks = dict(zip(parts[1::2], (block.strip() for block in parts[2::2])))

    if set(blocks) != set(SECTIONS):
        raise RuntimeError(
            "fallback_sections.tex.jinja must hold exactly one block per section in "
            f"SECTIONS; it has {sorted(blocks)} against {sorted(SECTIONS)}."
        )
    return blocks


FALLBACK_SECTIONS = _fallback_sections()

# The resume that has every section, so what a template omits is visible in one render.
COVERAGE_RESUME = "resume_kitchen_sink"


def fill_missing_sections(candidate: str) -> str:
    """Add our own block for every section this template would not print.

    A design showing four kinds of thing converts into a template that renders,
    compiles, and silently drops the publications, certifications and awards of everyone
    who uses it. Filling the gaps here rather than asking the model to invent sections it
    has never seen is both more reliable and cheaper: measured against real documents,
    demanding all eight sections up front cost conversions that had worked.

    What to print is fixed; the one thing that has to follow the design is the heading,
    which is the document's own \\section command.
    """
    escaped = escape_latex(load_resume(COVERAGE_RESUME))
    absent = missing_sections(COVERAGE_RESUME, escaped, candidate)
    if not absent:
        return candidate

    blocks = "\n\n".join(FALLBACK_SECTIONS[section] for section in absent)
    # Written with \section*, which is what an article-based design uses and styles. A
    # design numbering its sections defines \section only, and \section* there is an
    # "Undefined control sequence" — so follow whichever the document itself uses. Read
    # from the body alone: the preamble is full of \section in \titleformat and
    # \newcommand definitions, which say nothing about how the design writes a heading.
    _, _, printed_body = candidate.rpartition("\\begin{document}")
    if "\\section*" not in printed_body and "\\section{" in printed_body:
        blocks = blocks.replace("\\section*{", "\\section{")

    logger.info(f"Adding sections the design does not print: {', '.join(absent)}")
    head, end, tail = candidate.rpartition("\\end{document}")
    return f"{head}\n{blocks}\n{end}{tail}" if end else f"{candidate}\n{blocks}"


def verify(template_source: str, compile_pdf=generate_pdf_from_latex) -> str:
    """Render and compile the candidate against every reference resume.

    Returns the LaTeX engine that built them. Raises TemplatizationError describing
    the first failure, phrased so it can be handed straight back to the model.
    """
    renders: dict[str, str] = {}

    for name in VERIFICATION_RESUMES:
        # Escaped once and reused: what the template is given is what the checks below
        # have to look for. A name carrying `&` or `_` reaches the document escaped, and
        # looking for the raw form would fail a working template.
        escaped = escape_latex(load_resume(name))
        rendered = _render(f"the '{name}' resume", escaped, template_source)

        expected = escaped["personal_info"]["name"]
        if expected not in rendered:
            raise TemplatizationError(
                f"Rendering the '{name}' resume did not produce the candidate's name "
                f"({expected!r}), so the template is not reading the data it was given."
            )

        absent = missing_sections(name, escaped, template_source)
        if absent:
            raise TemplatizationError(
                f"Rendering the '{name}' resume produced nothing from its "
                f"{', '.join(absent)}, so a resume with those would lose them. Every "
                "section the data holds has to be rendered, even where the original "
                "document had no such section — add one in the same style it uses for "
                "the sections it does have."
            )

        renders[name] = rendered

    return _compile_with_a_working_engine(renders, compile_pdf)


def _ask_model(prompt: str) -> str:
    completion = client.chat.completions.create(
        model=TEMPLATIZER_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You convert LaTeX resumes into Jinja2 templates. You reply with "
                    "LaTeX only — no prose, no explanation, no markdown fences."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content or ""


def templatize(
    source_tex: str, *, ask=_ask_model, compile_pdf=generate_pdf_from_latex
) -> VerifiedTemplate:
    """Convert a complete .tex resume into a verified Jinja2 template.

    Raises TemplatizationError if no attempt renders and compiles.
    """
    preamble, body = relocate_personal_data(*split_document(source_tex))

    feedback = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        templated_body = _strip_fences(ask(build_prompt(preamble, body, feedback)))
        # The model's preamble is discarded in favour of ours, so the document's
        # setup is byte-identical to what the user uploaded no matter what it returns.
        candidate = f"{protect(preamble)}\n{templated_body}\n\\end{{document}}\n"

        try:
            # Before verification, because verification is what refuses a template that
            # would drop a section — and after this there should be none left to drop.
            candidate = fill_missing_sections(candidate)
            compiler = verify(candidate, compile_pdf=compile_pdf)
        except TemplatizationError as exc:
            logger.warning(
                f"Templatization attempt {attempt}/{MAX_ATTEMPTS} rejected: {exc}"
            )
            feedback = str(exc)
            continue

        logger.info(f"Templatization succeeded on attempt {attempt} with {compiler}")
        return VerifiedTemplate(candidate, compiler)

    raise TemplatizationError(
        f"Could not build a working template after {MAX_ATTEMPTS} attempts. "
        f"Last failure: {feedback}"
    )
