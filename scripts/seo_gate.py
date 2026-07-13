"""SEO gate: keeps the public web surface aligned with docs/seo-guidelines.md.

Runs in CI on pull_request (seo-gate.yml) only when SEO-relevant paths change
(public pages, landing components, robots/sitemap/llms.txt, public assets).
The guidelines doc is read verbatim at runtime, so maturing the rules is an
edit to that doc — no code change here.

Exit 0 = pass, 1 = flagged. The check is intentionally NOT in the required-
checks ruleset yet: a flag is a visible notification on the PR, not a merge
blocker. Promote it once the guidelines stabilize.
Maintainer override: the `seo-ok` label skips the gate (visible in the PR).
"""

import json
import os
import subprocess
import sys

MAX_DIFF_CHARS = 60_000
MODEL = os.environ.get("SEO_GATE_MODEL", "gpt-4.1")

VERDICT_SCHEMA = {
    "name": "SeoVerdict",
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

PROMPT = """You are the SEO gate for the Zumud repository. This PR touches \
the public web surface (pages, metadata, landing copy, crawl files, or \
content). Judge it ONLY against the SEO guidelines below — not for bugs, \
style, or scope (other gates do that).

The guidelines (enforce their letter and spirit):
---
{guidelines}
---

Verdict rules: "pass" unless you can point at a concrete guideline \
violation visible in the diff; when you flag, each reason must name the \
guideline rule and the specific file/hunk, and say what to change. Do not \
flag for things you merely cannot verify from the diff (e.g. whether an \
image asset is really 1200x630), and do not invent requirements that are \
not in the guidelines.

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
        print("No OPEN_AI_KEY available (fork PR?) — SEO gate skipped here.")
        return 0

    with open(os.environ["GITHUB_EVENT_PATH"]) as f:
        event = json.load(f)
    pr = event["pull_request"]

    labels = {label["name"] for label in pr.get("labels", [])}
    if "seo-ok" in labels:
        print("Label seo-ok present — maintainer override, gate skipped.")
        return 0

    base = pr["base"]["sha"]
    files = sh("git", "diff", "--name-status", f"{base}...HEAD")
    diff = sh("git", "diff", f"{base}...HEAD")
    truncated_note = ""
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS]
        truncated_note = " (truncated; judge what is visible plus the file list)"

    with open("docs/seo-guidelines.md") as f:
        guidelines = f.read()

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_schema", "json_schema": VERDICT_SCHEMA},
        messages=[
            {
                "role": "user",
                "content": PROMPT.format(
                    guidelines=guidelines,
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

    lines = [f"## SEO gate: {verdict['verdict'].upper()}", "", verdict["summary"]]
    lines += [f"- {reason}" for reason in verdict["reasons"]]
    if verdict["verdict"] == "flag":
        lines += [
            "",
            "Fix per docs/seo-guidelines.md (see reasons). Maintainer "
            "override: add the `seo-ok` label.",
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
