"""LaTeX escaping of AI-authored content.

`escape_latex` is the only thing between model output and the compiler, so every
special character needs its own case. The previous implementation chained
`str.replace` calls, which re-scanned text it had just inserted: a backslash became
`\\textbackslash{}` and the braces in that replacement were then escaped again,
rendering as `\\{}`. The other eleven rules were correct only because they happened
to run after the brace rules, which made the ordering load-bearing and undocumented.
"""

import pytest

from backend.utils.file_ops import escape_latex


@pytest.mark.parametrize(
    "raw, escaped",
    [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("<", r"\textless{}"),
        (">", r"\textgreater{}"),
    ],
)
def test_each_special_character_escapes_to_itself(raw, escaped):
    assert escape_latex(raw) == escaped


def test_a_replacement_is_never_escaped_again():
    """The regression: braces introduced by the backslash rule must survive."""
    assert escape_latex("C:\\Users") == r"C:\textbackslash{}Users"
    assert escape_latex("a\\b\\c") == r"a\textbackslash{}b\textbackslash{}c"


def test_realistic_resume_text():
    assert escape_latex("Cut costs by 40% (~$1.2M) across R&D") == (
        r"Cut costs by 40\% (\textasciitilde{}\$1.2M) across R\&D"
    )


def test_ordinary_text_is_untouched():
    assert escape_latex("Senior Engineer, Reykjavík — 2021–2024") == (
        "Senior Engineer, Reykjavík — 2021–2024"
    )


def test_nested_structures_are_escaped_throughout():
    escaped = escape_latex(
        {
            "personal_info": {"name": "A&B"},
            "skills": [{"category": "C#", "items": ["100%", "x_y"]}],
            "count": 3,
            "missing": None,
        }
    )

    assert escaped["personal_info"]["name"] == r"A\&B"
    assert escaped["skills"][0]["category"] == r"C\#"
    assert escaped["skills"][0]["items"] == [r"100\%", r"x\_y"]
    # Non-string leaves pass through so templates can still test truthiness.
    assert escaped["count"] == 3
    assert escaped["missing"] is None
