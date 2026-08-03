"""Resolving which template a user's resumes render with.

Selection is a single slug on `tailoring_options.resume_template` — see
`backend.models.templates` for the two forms it takes. Anything that cannot be
resolved (a retired built-in, a template the user deleted, a slug naming someone
else's row) falls back to the default: a stale preference must never fail a
generation the user is waiting on.
"""

from sqlalchemy.orm import Session

from backend.models import db_models
from backend.models.templates import (
    BUILTIN_PREFIX,
    DEFAULT_BUILTIN_SLUG,
    DEFAULT_TEMPLATE,
    USER_PREFIX,
    builtin_template,
)
from backend.utils.log import logger


def selected_slug(user_id: int | None, db: Session | None) -> str:
    """The slug a user has selected, or the default when they have no preference."""
    if not (user_id and db):
        return DEFAULT_TEMPLATE

    options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == user_id)
        .first()
    )
    return options.resume_template if options else DEFAULT_TEMPLATE


def _user_template(slug: str, user_id: int | None, db: Session | None) -> dict | None:
    if not (user_id and db):
        return None
    try:
        template_id = int(slug.removeprefix(USER_PREFIX))
    except ValueError:
        return None

    row = (
        db.query(db_models.UserTemplate)
        .filter(
            db_models.UserTemplate.id == template_id,
            # Scoped to the owner, so a stale or tampered slug can never render
            # another user's template.
            db_models.UserTemplate.user_id == user_id,
        )
        .first()
    )
    if row is None:
        return None
    return {"structure": row.latex_content, "compiler": row.compiler}


def resolve_template(user_id: int | None = None, db: Session | None = None) -> dict:
    """Load the template to render with, as a dict of 'structure' and 'compiler'."""
    slug = selected_slug(user_id, db)

    if slug.startswith(USER_PREFIX):
        template = _user_template(slug, user_id, db)
    else:
        template = builtin_template(slug.removeprefix(BUILTIN_PREFIX))

    if template is None:
        logger.warning(
            f"Template {slug!r} could not be resolved for user {user_id}; "
            f"falling back to {DEFAULT_TEMPLATE!r}"
        )
        return builtin_template(DEFAULT_BUILTIN_SLUG)

    return template
