"""Small, conservative checks for conspicuous machine-written output.

This is deliberately not an "AI detector". It catches objective output leaks and a
short list of expressions the product explicitly asks the model not to use. Broader
style judgments stay in the prompt so ordinary professional language is not rejected.
"""

import json
import re
from collections.abc import Iterator

_ISSUE_PATTERNS = (
    (
        "an internal citation or tool marker",
        re.compile(
            r"contentReference|oaicite|oai_citation|turn\d+(?:search|image|news|file)\d+|"
            r"\[cite:\s*\d|\[span_\d+\]|grok[_-](?:card|render)|:::writing",
            re.IGNORECASE,
        ),
        False,
    ),
    (
        "placeholder text",
        re.compile(
            r"\[(?:your|company|recruiter|hiring manager|insert|add|specific)[^\]]*\]|"
            r"\b(?:INSERT|PASTE)_[A-Z0-9_]+\b|20\d\d-[Xx]{2}-[Xx]{2}",
            re.IGNORECASE,
        ),
        False,
    ),
    ("an em dash", re.compile("\u2014"), False),
    ("curly quotation marks", re.compile("[\u2018\u2019\u201c\u201d]"), False),
    (
        "emoji or decorative symbols",
        re.compile("[\u2600-\u27bf\U0001f300-\U0001faff]"),
        True,
    ),
    (
        "Markdown formatting",
        re.compile(
            r"(?m)^\s{0,3}#{1,6}\s|\*\*|__|^\s*[-*]\s+\*\*|"
            r"^\s*[-*_]{3,}\s*$|^\s*\|.*\|\s*$"
        ),
        True,
    ),
    (
        "a canned opening",
        re.compile(
            r"\bI am (?:writing to (?:apply|express my interest)|excited to apply)\b|"
            r"\b(?:Certainly|Of course)[,!]?\s+(?:here|I)\b",
            re.IGNORECASE,
        ),
        True,
    ),
    (
        "stock promotional or AI wording",
        re.compile(
            r"\b(?:delve|tapestry|seamlessly|multifaceted|results-driven|"
            r"game-changer|groundbreaking)\b|\bproven track record\b|"
            r"\bpivotal (?:role|moment|part|contribution|shift)\b|"
            r"\bever-evolving landscape\b|\btestament to\b|\baligns perfectly\b|"
            r"\b(?:showcases?|underscores?)\b",
            re.IGNORECASE,
        ),
        True,
    ),
    (
        "a formulaic contrast",
        re.compile(
            r"\bnot\s+(?:only|just)\b.{0,100}\bbut(?:\s+also)?\b", re.IGNORECASE
        ),
        True,
    ),
    (
        "a formulaic transition",
        re.compile(
            r"(?m)(?:^|[.!?]\s+)(?:Moreover|Furthermore|Additionally),", re.IGNORECASE
        ),
        True,
    ),
)


_PROSE_FIELDS = {
    None,
    "tailored_answer",
    "tailored_coverletter",
    "summary",
    "description",
    "achievements",
    "items",
}


def _text_values(
    value: object, field: str | None = None
) -> Iterator[tuple[str | None, str]]:
    if isinstance(value, str):
        yield field, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _text_values(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from _text_values(child, field)


def _content_text(payload: str) -> Iterator[tuple[str | None, str]]:
    """Yield response text fields without treating JSON keys as prose."""
    try:
        parsed = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        yield None, payload
        return

    yield from _text_values(parsed)


def find_writing_quality_issues(payload: str) -> list[str]:
    """Return distinct, actionable issues found in generated response content."""
    issues: list[str] = []
    values = tuple(_content_text(payload))
    for label, pattern, prose_only in _ISSUE_PATTERNS:
        if any(
            pattern.search(value)
            for field, value in values
            if not prose_only or field in _PROSE_FIELDS
        ):
            issues.append(label)
    return issues


def quality_retry_instruction(issues: list[str]) -> str:
    joined = ", ".join(issues)
    return (
        "Revise the previous response because it contains "
        f"{joined}. Preserve every supported fact, the requested meaning, and the exact "
        "response schema. Change only the wording or formatting needed to fix those "
        "issues. Do not add facts, commentary, headings, or placeholders. Return the "
        "complete corrected response."
    )
