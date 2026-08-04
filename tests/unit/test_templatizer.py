"""Converting a user's .tex into a template.

The model is stubbed here — what is under test is everything around it: that the
preamble cannot be altered, that a bad candidate is rejected for the right reason,
and that the reason is fed back and retried rather than stored.
"""

import pytest

from backend.core import templatizer
from backend.core.templatizer import (
    MAX_ATTEMPTS,
    SECTIONS,
    TemplatizationError,
    build_prompt,
    fill_missing_sections,
    missing_sections,
    relocate_personal_data,
    split_document,
    templatize,
    verify,
)
from backend.fixtures import load_resume
from backend.models.templates import builtin_template
from backend.utils.file_ops import escape_latex
from backend.utils.jinja_env import render_resume_template
from tests.templatized_body import COMPLETE_BODY, DESIGN_BODY

PREAMBLE = "\\documentclass{article}\n\\usepackage{xcolor}\n\\begin{document}"

# A body has to cover every section to be accepted at all, so the good candidate is the
# shared one rather than a sketch. See tests/templatized_body.py.
GOOD_BODY = COMPLETE_BODY

# Covers everything except the publications, which verification has to notice: it
# renders, it carries the name, and it compiles.
BODY_MISSING_A_SECTION = COMPLETE_BODY.replace(
    "{% if publications %}", "{% if false %}"
)

# The trap the prompt warns about: `.items` finds dict.items, not the field.
BODY_WITH_ITEMS_COLLISION = """
{{ personal_info.name }}
{% if skills %}{% for group in skills %}{{ group.items|join(', ') }}{% endfor %}{% endif %}
"""

STATIC_BODY = "\\section*{Experience}\nJohn Doe, Acme Corp\n"


def compiles_fine(save_folder, latex, compiler):
    return object()


def always_fails(save_folder, latex, compiler):
    raise ValueError("! Undefined control sequence \\faPhone")


def test_a_latex_macro_parameter_in_the_preamble_survives():
    """`\\newcommand{\\x}[1]{#1}` contains `{#`, which Jinja reads as a comment
    opener — so an ordinary preamble made the whole file unparseable."""
    preamble = "\\documentclass{article}\n\\newcommand{\\bf}[2]{\\textbf{#1}{#2}}\n\\begin{document}"

    result = templatize(
        f"{preamble}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: GOOD_BODY,
        compile_pdf=compiles_fine,
    )
    rendered = render_resume_template(
        result.source, escape_latex(load_resume("resume_minimal"))
    )

    assert "\\newcommand{\\bf}[2]{\\textbf{#1}{#2}}" in rendered


def test_an_upload_cannot_escape_the_frozen_preamble():
    """A .tex whose preamble contains `{% endraw %}` would otherwise close the block
    early and hand the rest of itself to Jinja as template source."""
    hostile = (
        "\\documentclass{article}\n"
        "% {% endraw %}{{ personal_info.email }}\n"
        "\\begin{document}"
    )

    result = templatize(
        f"{hostile}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: GOOD_BODY,
        compile_pdf=compiles_fine,
    )
    rendered = render_resume_template(
        result.source, escape_latex(load_resume("resume_kitchen_sink"))
    )

    # The tokens survive as the literal text they were, and the field beside them
    # was never substituted.
    assert "% {% endraw %}{{ personal_info.email }}" in rendered


def test_a_name_needing_escaping_still_counts_as_rendered():
    """The rendered document holds the escaped name, so looking for the raw one
    failed templates whose candidate happens to have `&` or `_` in their name."""
    resume = load_resume("resume_minimal")
    resume["personal_info"]["name"] = "Ana & Bob_Smith"

    rendered = render_resume_template("{{ personal_info.name }}", escape_latex(resume))

    assert rendered == "Ana \\& Bob\\_Smith"


def test_a_template_needing_xelatex_is_accepted():
    """Which engine a document needs is a property of its preamble — fontspec means
    xelatex — so a template is not broken merely because pdflatex refuses it."""
    attempted = []

    def only_xelatex(save_folder, latex, compiler):
        attempted.append(compiler)
        if compiler != "xelatex":
            raise ValueError("! LaTeX Error: fontspec requires either XeTeX or LuaTeX")
        return object()

    compiler = verify(
        f"{PREAMBLE}\n{GOOD_BODY}\n\\end{{document}}", compile_pdf=only_xelatex
    )

    assert compiler == "xelatex"
    assert attempted[0] == "pdflatex"


def test_a_template_no_engine_can_build_is_rejected():
    with pytest.raises(TemplatizationError, match="Undefined control sequence"):
        verify(f"{PREAMBLE}\n{GOOD_BODY}\n\\end{{document}}", compile_pdf=always_fails)


def test_the_prompt_warns_about_the_comment_collision():
    assert "{#" in build_prompt(PREAMBLE, STATIC_BODY)


def test_splits_at_the_document_boundary():
    preamble, body = split_document(f"{PREAMBLE}\nHello\n\\end{{document}}\n")

    assert preamble.endswith("\\begin{document}")
    assert preamble.startswith("\\documentclass")
    assert body.strip() == "Hello"


@pytest.mark.parametrize(
    "source, missing",
    [
        ("\\documentclass{article}\nno body here", "begin"),
        ("\\documentclass{article}\n\\begin{document}\nunterminated", "end"),
    ],
)
def test_incomplete_documents_are_rejected(source, missing):
    with pytest.raises(TemplatizationError, match=missing):
        split_document(source)


MODERNCV = """\\documentclass[11pt,a4paper,sans]{moderncv}
\\moderncvstyle{casual}
\\name{John}{Doe}
\\address{street and number}{postcode city}{country}
\\phone[mobile]{+1~(234)~567~890}
\\email{john@doe.org}
\\begin{document}
\\makecvtitle
\\end{document}
"""


def test_personal_details_declared_in_the_preamble_move_into_the_body():
    """moderncv sets the candidate before \\begin{document}; freezing that would put
    John Doe's name on every resume the template ever renders."""
    preamble, body = relocate_personal_data(*split_document(MODERNCV))

    assert "John" not in preamble
    assert "john@doe.org" not in preamble
    assert "\\name{John}{Doe}" in body
    assert "\\phone[mobile]{+1~(234)~567~890}" in body
    # The design is still frozen, and the body still starts a document.
    assert "\\moderncvstyle{casual}" in preamble
    assert preamble.rstrip().endswith("\\begin{document}")


def test_a_preamble_without_personal_details_is_left_alone():
    preamble, body = relocate_personal_data(
        *split_document(f"{PREAMBLE}\nx\n\\end{{document}}")
    )

    assert preamble == PREAMBLE
    assert body.strip() == "x"


def test_a_macro_named_after_a_personal_command_is_not_relocated():
    """`\\newcommand{\\name}` defines the design; only a bare `\\name{...}` sets data."""
    source = "\\documentclass{article}\n\\newcommand{\\name}[1]{\\textbf{#1}}\n\\begin{document}\nx\n\\end{document}"

    preamble, _ = relocate_personal_data(*split_document(source))

    assert "\\newcommand{\\name}[1]{\\textbf{#1}}" in preamble


def test_the_preamble_is_reattached_verbatim():
    """The model never gets to author the preamble, so a document's setup survives
    whatever it returns."""
    hostile = "\\documentclass{book}\n\\begin{document}\nI rewrote your preamble\n"

    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: f"{hostile}{GOOD_BODY}",
        compile_pdf=compiles_fine,
    )

    assert PREAMBLE in result.source
    assert "\\documentclass{book}" not in result.source.split("\\begin{document}")[0]
    assert result.source.rstrip().endswith("\\end{document}")
    # And it renders back out unchanged.
    rendered = render_resume_template(
        result.source, escape_latex(load_resume("resume_minimal"))
    )
    assert rendered.lstrip().startswith("\\documentclass{article}")


def test_a_verified_template_is_returned():
    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: GOOD_BODY,
        compile_pdf=compiles_fine,
    )

    assert "{{ personal_info.name }}" in result.source
    assert result.compiler == "pdflatex"
    verify(result.source, compile_pdf=compiles_fine)


def test_a_template_that_drops_a_section_is_rejected():
    """The quietest failure of all: the design had no publications, so the template has
    none either, and every user who has them loses them without being told."""
    with pytest.raises(TemplatizationError, match="publications"):
        verify(
            f"{PREAMBLE}\n{BODY_MISSING_A_SECTION}\n\\end{{document}}",
            compile_pdf=compiles_fine,
        )


def test_a_section_is_missing_even_when_its_words_appear_elsewhere():
    """Why coverage is measured by taking the section away rather than by searching.

    The reference resume's fourth employer is 'University of Iceland, School of
    Engineering' and its first degree is from the University of Iceland — so a template
    that prints jobs and no education still has the institution in its output, and
    looking for the words would call that covered.
    """
    name = "resume_kitchen_sink"
    escaped = escape_latex(load_resume(name))
    body = "{{ personal_info.name }}{% if experience %}{% for job in experience %}{{ job.company }}{% endfor %}{% endif %}"

    assert escaped["education"][0]["institution"] in render_resume_template(
        body, escaped
    )
    assert "education" in missing_sections(name, escaped, body)


def test_an_unguarded_section_is_reported_by_name():
    """Taking a section away to see if it is printed also asks whether the template
    survives without it — which is what a candidate who has none of that will do."""
    body = "{{ personal_info.name }}{% for job in experience %}{{ job.company }}{% endfor %}"

    with pytest.raises(TemplatizationError, match="without its experience"):
        missing_sections(
            "resume_kitchen_sink",
            escape_latex(load_resume("resume_kitchen_sink")),
            body,
        )


def test_the_sections_a_design_never_had_are_added_for_it():
    """A design showing a header and jobs is most designs. Converting one faithfully
    would otherwise mean everyone using it loses their degrees and publications."""
    filled = fill_missing_sections(f"{PREAMBLE}\n{DESIGN_BODY}\n\\end{{document}}")
    name = "resume_kitchen_sink"

    assert not missing_sections(name, escape_latex(load_resume(name)), filled)
    # Ours go before the end, so the document is still a document.
    assert filled.rstrip().endswith("\\end{document}")


def test_what_is_added_follows_the_design_s_own_heading():
    """`\\section*` is undefined in a class that numbers its sections, so a block written
    with one is an "Undefined control sequence" in half the documents people upload."""
    numbered = f"{PREAMBLE}\n\\section{{Experience}}\n{DESIGN_BODY}\n\\end{{document}}"

    assert "\\section*" not in fill_missing_sections(
        numbered.replace("section*", "section")
    )


def test_a_template_that_prints_everything_is_left_alone():
    """Nothing is added to a design that already covers the resume — the model's own
    version of a section is in the design's idiom, and ours is not."""
    complete = f"{PREAMBLE}\n{GOOD_BODY}\n\\end{{document}}"

    assert fill_missing_sections(complete) == complete


def test_a_faithful_conversion_becomes_a_complete_template():
    """The two halves together: the model converts what it sees, we supply the rest, and
    what gets stored is a template that prints every section of a resume."""
    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: DESIGN_BODY,
        compile_pdf=compiles_fine,
    )
    name = "resume_kitchen_sink"

    assert not missing_sections(name, escape_latex(load_resume(name)), result.source)
    assert all(f"{{% if {section} %}}" in result.source for section in SECTIONS)


def test_a_template_that_ignores_the_data_is_rejected():
    """The failure mode that compiles perfectly: the model returns the original
    document, so every user gets the first user's resume."""
    with pytest.raises(TemplatizationError, match="not reading the data"):
        verify(
            f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}", compile_pdf=compiles_fine
        )


def test_a_filter_applied_to_the_wrong_type_is_rejected():
    """`skill.items` returns dict.items rather than the field, and the join filter
    then raises TypeError from inside the stdlib — outside Jinja's own exceptions."""
    with pytest.raises(TemplatizationError, match="TypeError"):
        verify(
            f"{PREAMBLE}\n{BODY_WITH_ITEMS_COLLISION}\n\\end{{document}}",
            compile_pdf=compiles_fine,
        )


def test_the_prompt_warns_about_the_items_collision():
    assert "skill['items']" in build_prompt(PREAMBLE, STATIC_BODY)


def test_broken_jinja_is_rejected():
    with pytest.raises(TemplatizationError, match="rais|Error"):
        verify(
            f"{PREAMBLE}\n{{% for x in %}}\n\\end{{document}}",
            compile_pdf=compiles_fine,
        )


def test_latex_that_renders_to_double_braces_is_accepted():
    """`\\textbf{{Languages:} Python}` is ordinary LaTeX — a group inside a macro
    argument — and rejecting it as a stray Jinja tag failed good templates."""
    quirk = "{% if skills %}\\textbf{ {% for s in skills %}{ {{ s.category }}:} {% endfor %} }{% endif %}"

    # Beside a complete body, because verification wants every section covered and
    # what is under test here is only that the quirk is not mistaken for a Jinja tag.
    verify(
        f"{PREAMBLE}\n{quirk}\n{GOOD_BODY}\n\\end{{document}}",
        compile_pdf=compiles_fine,
    )


def test_a_template_may_use_the_do_extension():
    """Models reach for `{% do %}` to build a contact line out of the fields that
    happen to be present; verification has to run the same Jinja that generation
    does, or a template passes here and breaks for the user."""
    contact = "{% set parts = [] %}{% do parts.append(personal_info.name) %}{{ parts|join(' ') }}"

    verify(
        f"{PREAMBLE}\n{contact}\n{GOOD_BODY}\n\\end{{document}}",
        compile_pdf=compiles_fine,
    )


def test_a_template_that_does_not_compile_is_rejected():
    with pytest.raises(TemplatizationError, match="Compiling"):
        verify(f"{PREAMBLE}\n{GOOD_BODY}\n\\end{{document}}", compile_pdf=always_fails)


def test_markdown_fences_are_stripped():
    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: f"```latex\n{GOOD_BODY}\n```",
        compile_pdf=compiles_fine,
    )

    assert "```" not in result.source


def test_failures_are_fed_back_and_retried():
    prompts = []

    def flaky(prompt):
        prompts.append(prompt)
        return STATIC_BODY if len(prompts) == 1 else GOOD_BODY

    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=flaky,
        compile_pdf=compiles_fine,
    )

    assert len(prompts) == 2
    assert "rejected" in prompts[1]
    assert "not reading the data" in prompts[1]
    assert "{{ personal_info.name }}" in result.source


def test_it_gives_up_rather_than_storing_something_broken():
    attempts = []

    with pytest.raises(TemplatizationError, match=f"after {MAX_ATTEMPTS} attempts"):
        templatize(
            f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
            ask=lambda prompt: attempts.append(prompt) or STATIC_BODY,
            compile_pdf=compiles_fine,
        )

    assert len(attempts) == MAX_ATTEMPTS


def test_the_prompt_carries_the_schema_and_a_worked_example():
    prompt = build_prompt(PREAMBLE, STATIC_BODY)

    # The data contract the template is written against.
    assert "personal_info" in prompt and "achievements" in prompt
    # A known-good template of a different design, to copy the guarding style from.
    assert "{% if" in prompt
    # The preamble as read-only context, so it knows which macros exist.
    assert "READ-ONLY" in prompt and "\\usepackage{xcolor}" in prompt


def test_the_shipped_builtin_would_pass_its_own_verification():
    """The example we hold the model to has to meet the bar we set."""
    verify(builtin_template("mteck")["structure"], compile_pdf=compiles_fine)


def test_no_network_is_used_when_the_model_is_injected(monkeypatch):
    def explode(*args, **kwargs):
        raise AssertionError("templatize() reached the real OpenAI client")

    monkeypatch.setattr(templatizer.client.chat.completions, "create", explode)

    templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: GOOD_BODY,
        compile_pdf=compiles_fine,
    )
