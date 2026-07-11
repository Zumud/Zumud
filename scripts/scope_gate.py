"""Scope-coherence gate: the anti-slop check no off-the-shelf reviewer does.

Judges a PR against its own description and the repo working principles:
does it do exactly one thing, is the diff proportional to that thing, does it
introduce abstractions/helpers/config nobody asked for, does it duplicate
existing code, are new dependencies justified? There is deliberately no
line-count limit — a mechanical 2,000-line rename passes, a 60-line PR that
smuggles in a new pattern gets flagged.

Runs in CI on pull_request (scope-gate.yml). Exit 0 = pass, 1 = flagged.
Maintainer override: the `scope-ok` label skips the gate (visible in the PR).
"""

import json
import os
import subprocess
import sys

MAX_DIFF_CHARS = 60_000
MODEL = os.environ.get("SCOPE_GATE_MODEL", "gpt-4.1")

VERDICT_SCHEMA = {
    "name": "ScopeVerdict",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "flag"]},
            "summary": {"type": "string"},
            "reasons": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["verdict", "summary", "reasons"],
        "additionalProperties": False,
    },
}

PROMPT = """You are the scope-coherence gate for the Zumud repository. Most \
changes here are written by AI agents and merge without human review, so you \
are the reviewer of last resort for scope discipline — not for bugs (other \
tools do that) and not for style (linters do that).

Judge the pull request ONLY on these questions:
1. Single purpose: does the diff do exactly one identifiable thing, and is it \
the thing the title/description says?
2. Proportionality: is the amount and shape of change proportional to that \
purpose? Mechanical bulk (renames, formatting, generated files, lockfiles) is \
fine when the description says so.
3. Unrequested additions: new abstractions, helpers, wrappers, config \
options, feature flags, or "future-proofing" that the purpose does not need.
4. Reuse: does it duplicate logic that plainly already exists in the diff \
context instead of reusing it?
5. Dependencies: any new package must be clearly justified by the purpose.

The repository's working principles (enforce their spirit):
---
{principles}
---

Verdict rules: "pass" unless you can point at a concrete violation; when you \
flag, each reason must reference a specific file/hunk and say what to split \
out or remove. Do not flag for missing tests, style, naming taste, or things \
you merely cannot verify from the diff.

PULL REQUEST
Title: {title}
Description:
{body}

Changed files:
{files}

Diff{truncated_note}:
{diff}
"""


def sh(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def main() -> int:
    api_key = os.environ.get("OPEN_AI_KEY", "")
    if not api_key:
        print(
            "No OPEN_AI_KEY available (fork PR?) — scope gate skipped here; "
            "it applies in the merge queue context."
        )
        return 0

    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    pr = event["pull_request"]

    labels = {label["name"] for label in pr.get("labels", [])}
    if "scope-ok" in labels:
        print("Label scope-ok present — maintainer override, gate skipped.")
        return 0

    base = pr["base"]["sha"]
    files = sh("git", "diff", "--name-status", f"{base}...HEAD")
    diff = sh("git", "diff", f"{base}...HEAD")
    truncated_note = ""
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        truncated_note = " (truncated; judge what is visible plus the file list)"

    with open(".cursor/rules/principles.mdc") as f:
        principles = f.read()

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_schema", "json_schema": VERDICT_SCHEMA},
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(
                    principles=principles,
                    title=pr.get("title") or "(none)",
                    body=pr.get("body") or "(none)",
                    files=files,
                    diff=diff,
                    truncated_note=truncated_note,
                ),
            }
        ],
    )
    verdict = json.loads(completion.choices[0].message.content)

    lines = [f"## Scope gate: {verdict['verdict'].upper()}", "", verdict["summary"]]
    lines += [f"- {reason}" for reason in verdict["reasons"]]
    if verdict["verdict"] == "flag":
        lines += [
            "",
            "Split or justify (see reasons). Maintainer override: "
            "add the `scope-ok` label.",
        ]
    report = "\n".join(lines)
    print(report)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write(report + "\n")

    return 0 if verdict["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
