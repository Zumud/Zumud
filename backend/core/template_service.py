"""The templates a user owns, picks between, and renders with.

Selection is a single slug on `tailoring_options.resume_template` — see
`backend.models.templates` for the two forms it takes. Anything that cannot be
resolved (a retired built-in, a template the user deleted, a slug naming someone
else's row) falls back to the default: a stale preference must never fail a
generation the user is waiting on.

Uploads are the same idea one step earlier. Converting a .tex into a template costs
several model attempts and a real compile each time, so the row is created `pending`
and finished off the request. Until it is `ready` it is visible but not selectable,
and a failure is recorded on the row rather than lost — the row is the only way back
to the person who uploaded it.
"""

from sqlalchemy.orm import Session

from backend.core.templatizer import TemplatizationError, templatize
from backend.models import db_models
from backend.models.db import SessionLocal
from backend.models.tailoring_options import TailoringOptionsBase
from backend.models.templates import (
    BUILTIN_PREFIX,
    BUILTINS,
    DEFAULT_BUILTIN_SLUG,
    DEFAULT_TEMPLATE,
    FAILED,
    PENDING,
    READY,
    USER_PREFIX,
    builtin_template,
)
from backend.utils.log import logger

# A resume class runs to a few tens of kilobytes; a megabyte of "LaTeX" is not a
# resume, and every upload costs model calls to convert.
MAX_UPLOAD_BYTES = 256 * 1024

# Enough to keep a couple of designs around without turning the converter into an
# open-ended bill.
MAX_TEMPLATES_PER_USER = 5


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


def _owned_row(
    slug: str, user_id: int | None, db: Session | None
) -> db_models.UserTemplate | None:
    """The row a `user:<id>` slug names, whatever its status, if it is this user's."""
    if not (user_id and db):
        return None
    try:
        template_id = int(slug.removeprefix(USER_PREFIX))
    except ValueError:
        return None

    return (
        db.query(db_models.UserTemplate)
        .filter(
            db_models.UserTemplate.id == template_id,
            # Scoped to the owner, so a stale or tampered slug can never reach
            # another user's template.
            db_models.UserTemplate.user_id == user_id,
        )
        .first()
    )


def _user_template(slug: str, user_id: int | None, db: Session | None) -> dict | None:
    row = _owned_row(slug, user_id, db)
    # A pending row has no template yet and a failed one never will, so neither can
    # be rendered or selected — callers treat None as "fall back to the default".
    if row is None or row.status != READY:
        return None
    return {"structure": row.latex_content, "compiler": row.compiler}


def _user_templates(user_id: int, db: Session) -> list[db_models.UserTemplate]:
    return (
        db.query(db_models.UserTemplate)
        .filter(db_models.UserTemplate.user_id == user_id)
        .order_by(db_models.UserTemplate.id.asc())
        .all()
    )


def available_templates(user_id: int, db: Session) -> list[dict]:
    """Every template the user may pick, built-ins first, with the current choice."""
    chosen = selected_slug(user_id, db)

    gallery = [
        {
            "slug": f"{BUILTIN_PREFIX}{slug}",
            "name": spec["name"],
            "description": spec["description"],
            # Built-in thumbnails are committed static assets; a user's own template
            # gets its preview when the upload is verified.
            "preview_url": f"/templates/{slug}.png",
            "status": READY,
            "error": None,
        }
        for slug, spec in BUILTINS.items()
    ]
    gallery += [
        {
            "slug": f"{USER_PREFIX}{row.id}",
            "name": row.name or "Your template",
            "description": "Your own LaTeX, converted into a template.",
            "preview_url": None,
            # The client polls this list while a conversion runs, so an upload's
            # progress and its failure both have to be visible here.
            "status": row.status,
            "error": row.error,
        }
        for row in _user_templates(user_id, db)
    ]

    for template in gallery:
        template["selected"] = template["slug"] == chosen
    # A slug we cannot resolve renders as the default, so show that rather than a
    # gallery where nothing at all looks chosen.
    if not any(template["selected"] for template in gallery):
        for template in gallery:
            template["selected"] = template["slug"] == DEFAULT_TEMPLATE

    return gallery


def select_template(slug: str, user_id: int, db: Session) -> None:
    """Record the user's choice, or raise ValueError if the slug is not theirs."""
    if slug.startswith(USER_PREFIX):
        exists = _user_template(slug, user_id, db) is not None
    else:
        exists = builtin_template(slug.removeprefix(BUILTIN_PREFIX)) is not None
    if not exists:
        raise ValueError(f"{slug!r} is not a template you can select.")

    options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == user_id)
        .first()
    )
    if options is None:
        # A user with no row runs on TailoringOptionsBase's defaults, and the column
        # default for ai_model is a *different*, cheaper model — so creating the row
        # implicitly would quietly downgrade every generation they make afterwards.
        # Picking a template must not change which model writes their resume.
        options = db_models.TailoringOptions(
            user_id=user_id, ai_model=TailoringOptionsBase().ai_model
        )
        db.add(options)
    options.resume_template = slug
    db.commit()


def decode_tex(filename: str, raw: bytes) -> str:
    """The upload as LaTeX source, or ValueError worded for the person who sent it.

    Cheap checks that a file is even a candidate, so an upload that could never work
    is refused immediately instead of costing a conversion to find out.
    """
    if not filename.lower().endswith(".tex"):
        raise ValueError("Upload the .tex source of your resume.")
    if not raw:
        raise ValueError("That file is empty.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError(
            f"That file is larger than {MAX_UPLOAD_BYTES // 1024}KB. "
            "Upload just the .tex source, without its images or fonts."
        )

    # Plenty of real .tex files predate UTF-8, and latin-1 accepts any byte sequence,
    # so decoding always succeeds — which is fine, because it is the shape check below
    # that turns away something that was never a document.
    try:
        source = raw.decode("utf-8")
    except UnicodeDecodeError:
        source = raw.decode("latin-1")

    # The templatizer splits a document at \begin{document}; without that there is
    # nothing to convert. A class or style file alone is the common mistake.
    if "\\documentclass" not in source or "\\begin{document}" not in source:
        raise ValueError(
            "That does not look like a complete LaTeX document. It needs both "
            "\\documentclass and \\begin{document}."
        )
    return source


def accept_upload(
    filename: str, raw: bytes, name: str | None, user_id: int, db: Session
) -> db_models.UserTemplate:
    """Record an uploaded .tex as a pending template, ready to be converted.

    Raises ValueError, worded for the user, if the file or their allowance says no.
    """
    source = decode_tex(filename, raw)

    rows = _user_templates(user_id, db)
    if any(row.status == PENDING for row in rows):
        raise ValueError("Your last upload is still being converted. Give it a moment.")

    # A failed row exists only to explain itself, and a fresh upload is that
    # explanation being acted on — so it stops counting against the allowance.
    for row in [row for row in rows if row.status == FAILED]:
        db.delete(row)
    kept = [row for row in rows if row.status != FAILED]
    if len(kept) >= MAX_TEMPLATES_PER_USER:
        raise ValueError(
            f"You already have {MAX_TEMPLATES_PER_USER} templates. "
            "Delete one to add another."
        )

    template = db_models.UserTemplate(
        user_id=user_id,
        name=(name or "").strip() or filename.removesuffix(".tex"),
        source_tex=source,
        status=PENDING,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template


def convert_upload(template_id: int) -> None:
    """Turn a pending upload into a usable template. Runs after the response.

    Nothing here may raise: this runs detached from any request, so the row is the
    only way to tell the user what happened.
    """
    db = SessionLocal()
    try:
        row = db.get(db_models.UserTemplate, template_id)
        if row is None or row.status != PENDING:
            return

        try:
            verified = templatize(row.source_tex)
        except TemplatizationError as exc:
            logger.info(f"Template {template_id} could not be converted: {exc}")
            row.status, row.error = FAILED, str(exc)
        except Exception:
            logger.exception(f"Converting template {template_id} raised")
            row.status, row.error = (
                FAILED,
                (
                    "Something went wrong converting that file. Try again, or a "
                    "different template."
                ),
            )
        else:
            row.latex_content = verified.source
            row.compiler = verified.compiler
            row.status, row.error = READY, None
            logger.info(f"Template {template_id} converted with {verified.compiler}")

        db.commit()
    finally:
        db.close()


def delete_template(slug: str, user_id: int, db: Session) -> None:
    """Remove one of the user's own templates, or raise ValueError if it isn't."""
    row = _owned_row(slug, user_id, db) if slug.startswith(USER_PREFIX) else None
    if row is None:
        raise ValueError(f"{slug!r} is not a template you can delete.")

    db.delete(row)
    # resolve_template would fall back on its own, but leaving a slug pointing at a
    # deleted row means the gallery and the generator disagree about what is in use.
    options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == user_id)
        .first()
    )
    if options is not None and options.resume_template == slug:
        options.resume_template = DEFAULT_TEMPLATE
    db.commit()


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
