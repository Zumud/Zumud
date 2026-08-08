"""Risk-tier gate: has this PR touched something a human has to look at?

The tier is worked out here, from the files the PR changes. It used to be read from the
`tier:T2` label, which cannot be trusted to have arrived: the labeler is a separate
workflow applying the label with GITHUB_TOKEN, and a token-driven label by design starts
no further workflow runs — so this check raced the labeler and passed vacuously whenever
it won. #210 and #212, both dependency changes, merged with no human step that way.

The paths are still the labeler's own, read from `.github/labeler.yml`, so the label a
human sees on the PR and the tier enforced here cannot come to describe different things.

Reads the changed paths on stdin, one per line. Exit 0 = tier 1, nothing to sign off;
exit 1 = tier 2, and the caller (t2-approval.yml) then requires maintainer sign-off.

    gh api "repos/$REPO/pulls/$PR/files" --paginate --jq '.[].filename' |
      python3 scripts/tier_gate.py
"""

import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / ".github/labeler.yml"

# The globs sit under this key in the labeler's config, one per line.
_KEY = "any-glob-to-any-file:"
_ENTRY = re.compile(r"^\s+- (\S+)\s*$")


def tier2_globs(config: str) -> list[str]:
    """The tier:T2 path globs, read without a YAML parser.

    A parser would mean a dependency in a job that otherwise needs nothing, for a file
    whose shape is a flat list. tests/unit/test_tier_gate.py holds this to what PyYAML
    makes of the same file, so the shortcut cannot quietly stop agreeing with it.
    """
    globs = []
    collecting = False
    for line in config.splitlines():
        if line.strip().startswith("#"):
            continue
        # The key is itself a list entry, so it arrives as "- any-glob-to-any-file:".
        if line.strip().removeprefix("- ") == _KEY:
            collecting = True
            continue
        if not collecting:
            continue
        entry = _ENTRY.match(line)
        if entry:
            globs.append(entry.group(1))
        elif line.strip():
            break
    return globs


def matches(path: str, glob: str) -> bool:
    """Whether one changed path is one of the sensitive ones.

    Only the two shapes the config uses — a whole directory and an exact file. Anything
    else raises rather than being approximated: a gate that silently under-matches a
    pattern it does not understand is worse than one that fails loudly.
    """
    if glob.endswith("/**"):
        return path.startswith(glob[:-2])
    if "*" in glob:
        raise ValueError(f"tier_gate cannot evaluate the glob {glob!r}")
    return path == glob


def sensitive_paths(paths: list[str], globs: list[str]) -> list[str]:
    return [path for path in paths if any(matches(path, glob) for glob in globs)]


def main() -> int:
    paths = [line.strip() for line in sys.stdin if line.strip()]
    matched = sensitive_paths(paths, tier2_globs(CONFIG.read_text(encoding="utf-8")))

    if not matched:
        print(f"Tier 1: none of the {len(paths)} changed files are sensitive.")
        return 0

    print("Tier 2 — this PR touches:")
    for path in matched:
        print(f"  {path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
