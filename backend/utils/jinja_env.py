"""The one environment that renders resume templates.

Verifying a template only means anything if verification runs it exactly the way
generation will, so both go through here rather than each building a `Template`
with its own settings.

Values are LaTeX-escaped by `escape_latex` before they get here; autoescaping is
Jinja's HTML feature and would corrupt them.
"""

from jinja2 import Environment

# `do` lets a template accumulate a list before emitting it — the natural way to
# join a variable number of contact fields into one line — and models reach for it
# unprompted. Without the extension the template merely fails to parse.
resume_env = Environment(extensions=["jinja2.ext.do"], autoescape=False)


def render_resume_template(source: str, data: dict) -> str:
    return resume_env.from_string(source).render(data)
