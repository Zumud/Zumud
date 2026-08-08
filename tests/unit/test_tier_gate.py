"""The gate that decides whether a PR needs a human.

It is the only human step in the merge policy, and it used to be decided by a label
another workflow races to apply. Now it reads the diff, which makes it worth testing:
under-matching here means an auth, billing, dependency or migration change merging with
nobody looking at it.
"""

import pytest
import yaml

from scripts.tier_gate import CONFIG, matches, sensitive_paths, tier2_globs

CONFIG_TEXT = CONFIG.read_text(encoding="utf-8")
GLOBS = tier2_globs(CONFIG_TEXT)


def test_the_globs_are_the_labelers_own():
    """The shortcut parser has to see exactly what a YAML parser sees.

    The gate reads .github/labeler.yml without PyYAML so its CI job needs no
    dependencies; this is what keeps that from drifting into a different list — and
    therefore the label a human reads from the tier actually enforced.
    """
    config = yaml.safe_load(CONFIG_TEXT)
    expected = config["tier:T2"][0]["changed-files"][0]["any-glob-to-any-file"]

    assert GLOBS == expected


def test_every_configured_glob_is_one_the_gate_understands():
    """A pattern shape it cannot evaluate must raise, and none is in use today."""
    for glob in GLOBS:
        assert matches("some/unrelated/file.py", glob) is False


def test_a_glob_it_cannot_evaluate_raises():
    with pytest.raises(ValueError, match="cannot evaluate"):
        matches("backend/api/auth.py", "backend/api/*.py")


@pytest.mark.parametrize(
    "path",
    [
        "requirements.txt",
        "frontend/package.json",
        # A bump under a transitive package touches nothing else — #219 moved
        # nanoid, js-yaml and dompurify and was waved through as tier 1.
        "frontend/package-lock.json",
        "backend/core/supabase_auth.py",
        "migrations/versions/23ef185de22c_baseline.py",
        ".github/workflows/ci.yml",
        "deploy/zumud-deploy.sh",
        "scripts/tier_gate.py",
    ],
)
def test_a_sensitive_change_is_tier_two(path):
    assert sensitive_paths([path], GLOBS) == [path]


@pytest.mark.parametrize(
    "path",
    [
        "backend/core/templatizer.py",
        "backend/templates/jake.tex.jinja",
        "frontend/src/components/profile/template-gallery.tsx",
        "tests/unit/test_tier_gate.py",
        "docs/dev-pipeline.md",
        # Prefix matching is per directory: these are not the sensitive ones.
        "deployment-notes.md",
        "scripts-for-me/thing.sh",
        "backend/api/authors.py",
    ],
)
def test_an_ordinary_change_is_tier_one(path):
    assert sensitive_paths([path], GLOBS) == []


def test_one_sensitive_file_among_many_still_counts():
    """The failure this gate exists for: a big harmless-looking PR with a dependency
    bump in it."""
    paths = [f"frontend/src/app/page-{index}.tsx" for index in range(20)]

    assert sensitive_paths([*paths, "requirements.txt"], GLOBS) == ["requirements.txt"]


def test_an_empty_diff_is_tier_one():
    assert sensitive_paths([], GLOBS) == []
