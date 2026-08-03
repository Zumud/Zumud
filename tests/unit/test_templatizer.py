"""Converting a user's .tex into a template.

The model is stubbed here — what is under test is everything around it: that the
preamble cannot be altered, that a bad candidate is rejected for the right reason,
and that the reason is fed back and retried rather than stored.
"""

import pytest
from jinja2 import Template

from backend.core import templatizer
from backend.core.templatizer import (
    MAX_ATTEMPTS,
    TemplatizationError,
    build_prompt,
    split_document,
    templatize,
    verify,
)
from backend.fixtures import load_resume
from backend.models.templates import builtin_template
from backend.utils.file_ops import escape_latex

PREAMBLE = "\\documentclass{article}\n\\usepackage{xcolor}\n\\begin{document}"

GOOD_BODY = """
{{ personal_info.name }}
{% if experience %}
\\section*{Experience}
{% for job in experience %}\\textbf{ {{ job.company }} }{% if job.role %} — {{ job.role }}{% endif %}
{% endfor %}
{% endif %}
{% if skills %}\\section*{Skills}{% for group in skills %}{{ group['items']|join(', ') }}{% endfor %}{% endif %}
"""

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
    rendered = Template(result).render(escape_latex(load_resume("resume_minimal")))

    assert "\\newcommand{\\bf}[2]{\\textbf{#1}{#2}}" in rendered


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


def test_the_preamble_is_reattached_verbatim():
    """The model never gets to author the preamble, so a document's setup survives
    whatever it returns."""
    hostile = "\\documentclass{book}\n\\begin{document}\nI rewrote your preamble\n"

    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: f"{hostile}{GOOD_BODY}",
        compile_pdf=compiles_fine,
    )

    assert PREAMBLE in result
    assert "\\documentclass{book}" not in result.split("\\begin{document}")[0]
    assert result.rstrip().endswith("\\end{document}")
    # And it renders back out unchanged.
    rendered = Template(result).render(escape_latex(load_resume("resume_minimal")))
    assert rendered.lstrip().startswith("\\documentclass{article}")


def test_a_verified_template_is_returned():
    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: GOOD_BODY,
        compile_pdf=compiles_fine,
    )

    assert "{{ personal_info.name }}" in result
    verify(result, compile_pdf=compiles_fine)


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


def test_a_template_that_does_not_compile_is_rejected():
    with pytest.raises(TemplatizationError, match="Compiling"):
        verify(f"{PREAMBLE}\n{GOOD_BODY}\n\\end{{document}}", compile_pdf=always_fails)


def test_markdown_fences_are_stripped():
    result = templatize(
        f"{PREAMBLE}\n{STATIC_BODY}\n\\end{{document}}",
        ask=lambda prompt: f"```latex\n{GOOD_BODY}\n```",
        compile_pdf=compiles_fine,
    )

    assert "```" not in result


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
    assert "{{ personal_info.name }}" in result


def test_it_gives_up_rather_than_storing_something_broken():
    attempts = []

    with pytest.raises(TemplatizationError, match="after 3 attempts"):
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
