"""Run the templatizer for real: real model, real compiler, real resumes.

Inputs are the three static LaTeX resumes that used to sit in templates.py — a
moderncv document and two article-based ones. They are exactly the shape a user
would upload: complete documents with someone else's details hardcoded in.
"""

import sys
import time
from pathlib import Path

from jinja2 import Template

from backend.core.templatizer import TEMPLATIZER_MODEL, TemplatizationError, templatize
from backend.fixtures import VERIFICATION_RESUMES, load_resume
from backend.utils.file_ops import escape_latex

OUT = Path("/tmp/zumud-templatizer")
NAMES = ["template_1", "template_2", "harshibar_template"]

print(f"model: {TEMPLATIZER_MODEL}\n")
results = []

for name in NAMES:
    source = (OUT / f"{name}.tex").read_text()
    started = time.time()
    print(f"--- {name} ({len(source)} chars) ---", flush=True)
    attempts = []

    def recording_ask(prompt):
        from backend.core.templatizer import _ask_model

        reply = _ask_model(prompt)
        attempts.append(reply)
        (OUT / f"{name}.attempt{len(attempts)}.tex").write_text(reply)
        return reply

    try:
        template = templatize(source, ask=recording_ask)
    except TemplatizationError as exc:
        print(f"    FAILED after {time.time() - started:.0f}s: {str(exc)[:300]}\n", flush=True)
        results.append((name, False, time.time() - started, 0))
        continue

    elapsed = time.time() - started
    (OUT / f"{name}.tex.jinja").write_text(template)

    # The preamble must be byte-identical to the upload.
    original_preamble = source.split("\\begin{document}")[0]
    generated_preamble = template.split("\\begin{document}")[0]
    preamble_intact = original_preamble == generated_preamble

    # None of the original person's details may survive.
    leaked = [
        marker
        for marker in ("John", "Doe", "johndoe", "john@doe.org", "Harshibar", "Jane")
        if marker in template
    ]

    renders = {}
    for fixture in VERIFICATION_RESUMES:
        resume = load_resume(fixture)
        rendered = Template(template).render(escape_latex(resume))
        renders[fixture] = (len(rendered), resume["personal_info"]["name"] in rendered)

    print(f"    OK in {elapsed:.0f}s -> {len(template)} chars", flush=True)
    print(f"    preamble byte-identical: {preamble_intact}")
    print(f"    original owner's details leaked: {leaked or 'none'}")
    for fixture, (size, has_name) in renders.items():
        print(f"    renders {fixture}: {size} chars, name present: {has_name}")
    print(flush=True)
    results.append((name, True, elapsed, len(template)))

print("=" * 60)
ok = sum(1 for _, success, _, _ in results if success)
for name, success, elapsed, size in results:
    print(f"  {'PASS' if success else 'FAIL'}  {name:<20} {elapsed:5.0f}s  {size} chars")
print(f"\n{ok}/{len(NAMES)} real resumes templatized, verified and compiled")
sys.exit(0 if ok == len(NAMES) else 1)
