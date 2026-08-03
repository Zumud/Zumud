"""Turning a user's LaTeX resume into a template we can render anyone's data into.

The hard part is that the output has to be a working Jinja2 program, not merely
plausible LaTeX, and a model asked to rewrite a whole document will happily reword a
package option or drop a macro definition and produce something that no longer
compiles. Two things keep that in check:

*Freeze the preamble.* Everything up to `\\begin{document}` is passed to the model as
read-only context — so it knows which macros the document defines — and then our copy
is reattached verbatim. The model only ever authors the body, so it cannot break the
document's setup even if it tries.

*Verify before accepting.* A candidate is rendered against both reference resumes and
actually compiled. Anything that fails — a syntax error, an unrendered tag, a
compiler error, or a template that quietly ignores the data it was given — goes back
to the model as feedback, up to MAX_ATTEMPTS times. Nothing is stored until it has
produced a real PDF from both fixtures.
"""

import re
import tempfile

from jinja2 import Template
from openai import OpenAI

from backend.config.envs import OPEN_AI_KEY
from backend.fixtures import VERIFICATION_RESUMES, load_resume
from backend.models.ai_models import AIModel
from backend.models.resume_models import StructuredResume
from backend.models.templates import builtin_template
from backend.utils.file_ops import escape_latex, generate_pdf_from_latex
from backend.utils.log import logger

MAX_ATTEMPTS = 3

# Templatizing is a harder, rarer task than tailoring, so it does not follow the
# user's chosen tailoring model.
TEMPLATIZER_MODEL = AIModel.gpt_4_1_mini

BEGIN_DOCUMENT = re.compile(r"\\begin\s*\{document\}")
END_DOCUMENT = re.compile(r"\\end\s*\{document\}")

client = OpenAI(api_key=OPEN_AI_KEY)


class TemplatizationError(Exception):
    """A user's .tex could not be turned into a template that renders and compiles."""


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


def protect(preamble: str) -> str:
    """Mark the preamble as literal text rather than template source.

    A LaTeX macro definition writes its parameters as `{#1}`, and Jinja reads `{#`
    as the start of a comment — so a preamble containing `\\newcommand{\\x}[1]{#1}`
    makes the whole file unparseable before any field is ever substituted. The
    preamble is by definition not templated, so saying so is both the smallest fix
    and the honest one. (The built-in template predates this and works around the
    same collision by hand, writing `{{ '{#' }}` at each site.)
    """
    return f"{{% raw %}}{preamble}{{% endraw %}}"


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
   "Education" heading with nothing under it is a defect.
5. The values are ALREADY LaTeX-escaped before rendering. Never add \textbackslash,
   \&, escaping filters, or |e. Use values as they are.
6. Use only macros that the preamble below already defines, plus standard LaTeX. Do
   not invent a macro and do not add \usepackage.
7. Keep the original's visual design: same sections in the same order, same spacing
   and typography. You are changing where the content comes from, not how it looks.
8. Write the list of skills as skill['items'], never skill.items. Jinja resolves an
   attribute before a key, and `.items` finds Python's dictionary method instead of
   the field — which renders as a method object rather than the skills.
9. `{#` opens a comment in Jinja, so a LaTeX group starting with a macro parameter —
   `{#1}` — makes the file unparseable. Write such a group as `{{ '{#' }}1}`. Never
   open a Jinja comment yourself.
"""


def _rules() -> str:
    return RULES % {"schema": StructuredResume.model_json_schema()}


def _worked_example() -> str:
    """The one template known to render both fixtures and compile."""
    _, body = split_document(builtin_template("mteck")["structure"])
    return (
        "Here is a body that satisfies all of the above, for a different design. "
        "Match this level of guarding and looping:\n\n"
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


def verify(template_source: str, compile_pdf=generate_pdf_from_latex):
    """Render and compile the candidate against every reference resume.

    Raises TemplatizationError describing the first failure, phrased so it can be
    handed straight back to the model.
    """
    for name in VERIFICATION_RESUMES:
        resume = load_resume(name)

        try:
            rendered = Template(template_source).render(escape_latex(resume))
        except Exception as exc:
            # Not just TemplateError: a template is arbitrary code to Jinja, and a
            # filter applied to the wrong type raises straight out of the stdlib.
            raise TemplatizationError(
                f"Rendering the '{name}' resume raised {type(exc).__name__}: {exc}"
            ) from exc

        if "{%" in rendered or "{{" in rendered:
            raise TemplatizationError(
                f"Rendering the '{name}' resume left un-executed Jinja tags in the "
                "output, so a tag is malformed."
            )

        expected = resume["personal_info"]["name"]
        if expected not in rendered:
            raise TemplatizationError(
                f"Rendering the '{name}' resume did not produce the candidate's name "
                f"({expected!r}), so the template is not reading the data it was given."
            )

        with tempfile.TemporaryDirectory() as tmp:
            try:
                compile_pdf(tmp, rendered, "pdflatex")
            except ValueError as exc:
                raise TemplatizationError(
                    f"Compiling the '{name}' resume failed:\n{exc}"
                ) from exc


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
) -> str:
    """Convert a complete .tex resume into a verified Jinja2 template.

    Raises TemplatizationError if no attempt renders and compiles.
    """
    preamble, body = split_document(source_tex)

    feedback = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        templated_body = _strip_fences(ask(build_prompt(preamble, body, feedback)))
        # The model's preamble is discarded in favour of ours, so the document's
        # setup is byte-identical to what the user uploaded no matter what it returns.
        candidate = f"{protect(preamble)}\n{templated_body}\n\\end{{document}}\n"

        try:
            verify(candidate, compile_pdf=compile_pdf)
        except TemplatizationError as exc:
            logger.warning(
                f"Templatization attempt {attempt}/{MAX_ATTEMPTS} rejected: {exc}"
            )
            feedback = str(exc)
            continue

        logger.info(f"Templatization succeeded on attempt {attempt}")
        return candidate

    raise TemplatizationError(
        f"Could not build a working template after {MAX_ATTEMPTS} attempts. "
        f"Last failure: {feedback}"
    )
