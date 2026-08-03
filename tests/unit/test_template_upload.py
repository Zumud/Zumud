"""Uploading a .tex and having it become a template the user can pick.

Two things matter here. A file that could never work should be refused before it
costs a conversion, with a reason the user can act on. And because conversion happens
after the response, its outcome — success or failure — has to end up on the row,
since that is the only way back to the person who uploaded it.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core import template_service
from backend.core.template_service import (
    MAX_TEMPLATES_PER_USER,
    MAX_UPLOAD_BYTES,
    accept_upload,
    available_templates,
    convert_upload,
    decode_tex,
    delete_template,
    resolve_template,
    select_template,
)
from backend.core.templatizer import TemplatizationError, VerifiedTemplate
from backend.models import db_models
from backend.models.db import Base
from backend.models.templates import DEFAULT_TEMPLATE, FAILED, PENDING, READY

DOCUMENT = b"\\documentclass{article}\\begin{document}Ada\\end{document}"


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def db(engine, monkeypatch):
    sessions = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # convert_upload runs detached from any request and opens its own session; point
    # it at the same in-memory database so the test can see what it wrote.
    monkeypatch.setattr(template_service, "SessionLocal", sessions)

    session = sessions()
    try:
        session.add_all(
            [
                db_models.User(id=1, username="ada", email="ada@example.com"),
                db_models.User(id=2, username="bob", email="bob@example.com"),
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()


def add_template(db, *, id, user_id=1, status=READY, name="Mine"):
    db.add(
        db_models.UserTemplate(
            id=id,
            user_id=user_id,
            name=name,
            latex_content="Hello {{ personal_info.name }}" if status == READY else None,
            compiler="pdflatex",
            status=status,
        )
    )
    db.commit()


def statuses(gallery):
    return {template["slug"]: template["status"] for template in gallery}


# --- what we refuse to even try -------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "raw", "reason"),
    [
        ("resume.pdf", DOCUMENT, "\\.tex source"),
        ("resume.tex", b"", "empty"),
        ("resume.tex", b"x" * (MAX_UPLOAD_BYTES + 1), "larger than"),
        ("resume.tex", b"\\documentclass{article}", "complete LaTeX document"),
        (
            "resume.tex",
            b"\\begin{document}hi\\end{document}",
            "complete LaTeX document",
        ),
    ],
)
def test_an_unusable_upload_is_refused_with_a_reason(filename, raw, reason):
    with pytest.raises(ValueError, match=reason):
        decode_tex(filename, raw)


def test_a_document_at_the_size_limit_is_still_accepted():
    padding = b"%" * (MAX_UPLOAD_BYTES - len(DOCUMENT))

    assert decode_tex("resume.tex", DOCUMENT + padding)


def test_latin_1_source_survives_decoding():
    """A .tex written in a legacy encoding is still a .tex; rejecting it as "not
    text" would turn a working upload away."""
    source = decode_tex("cv.tex", DOCUMENT.replace(b"Ada", b"Ren\xe9"))

    assert "René" in source


def test_binary_renamed_to_tex_is_refused():
    """Not for being undecodable — latin-1 decodes anything — but for containing no
    document, which is the check that actually means something."""
    with pytest.raises(ValueError, match="complete LaTeX document"):
        decode_tex("cv.tex", b"\xff\xfe\x00\x01" * 10)


# --- accepting one --------------------------------------------------------------


def test_an_accepted_upload_is_pending_and_keeps_the_source(db):
    template = accept_upload("cv.tex", DOCUMENT, None, 1, db)

    assert template.status == PENDING
    assert template.latex_content is None
    assert "\\documentclass" in template.source_tex


def test_the_filename_names_the_template_when_the_user_does_not(db):
    assert accept_upload("Ada's design.tex", DOCUMENT, "  ", 1, db).name == (
        "Ada's design"
    )


def test_a_given_name_wins(db):
    assert accept_upload("cv.tex", DOCUMENT, "Two column", 1, db).name == "Two column"


def test_a_second_upload_waits_for_the_first(db):
    accept_upload("cv.tex", DOCUMENT, None, 1, db)

    with pytest.raises(ValueError, match="still being converted"):
        accept_upload("other.tex", DOCUMENT, None, 1, db)


def test_the_allowance_is_enforced(db):
    for id in range(1, MAX_TEMPLATES_PER_USER + 1):
        add_template(db, id=id)

    with pytest.raises(ValueError, match="Delete one"):
        accept_upload("cv.tex", DOCUMENT, None, 1, db)


def test_a_failed_attempt_does_not_use_up_the_allowance(db):
    """Uploading again *is* the response to a failure, so the dead row that only
    existed to explain itself gets out of the way."""
    for id in range(1, MAX_TEMPLATES_PER_USER):
        add_template(db, id=id)
    add_template(db, id=99, status=FAILED)

    accept_upload("cv.tex", DOCUMENT, None, 1, db)

    assert db.get(db_models.UserTemplate, 99) is None


def test_another_users_templates_do_not_count_against_the_allowance(db):
    for id in range(1, MAX_TEMPLATES_PER_USER + 1):
        add_template(db, id=id, user_id=2)

    assert accept_upload("cv.tex", DOCUMENT, None, 1, db)


# --- converting it --------------------------------------------------------------


def test_a_converted_upload_becomes_usable(db, monkeypatch):
    monkeypatch.setattr(
        template_service,
        "templatize",
        lambda source: VerifiedTemplate("Hi {{ personal_info.name }}", "xelatex"),
    )
    template = accept_upload("cv.tex", DOCUMENT, None, 1, db)

    convert_upload(template.id)

    db.expire_all()
    assert template.status == READY
    assert template.latex_content == "Hi {{ personal_info.name }}"
    # Whichever engine verification found is the one generation has to use.
    assert template.compiler == "xelatex"
    assert template.error is None


def test_a_conversion_failure_is_explained_on_the_row(db, monkeypatch):
    def refuse(source):
        raise TemplatizationError("Compiling the 'minimal' resume failed: no \\name")

    monkeypatch.setattr(template_service, "templatize", refuse)
    template = accept_upload("cv.tex", DOCUMENT, None, 1, db)

    convert_upload(template.id)

    db.expire_all()
    assert template.status == FAILED
    assert "no \\name" in template.error


def test_an_unexpected_error_still_leaves_something_the_user_can_read(db, monkeypatch):
    def explode(source):
        raise RuntimeError("connection reset by peer")

    monkeypatch.setattr(template_service, "templatize", explode)
    template = accept_upload("cv.tex", DOCUMENT, None, 1, db)

    convert_upload(template.id)

    db.expire_all()
    assert template.status == FAILED
    # The internal cause is logged, not shown; a user cannot act on a socket error.
    assert "connection reset" not in template.error
    assert template.error


def test_converting_something_already_settled_does_nothing(db, monkeypatch):
    """Background tasks can be retried; a second run must not overwrite a template
    the user is already using."""
    add_template(db, id=3, status=READY)
    monkeypatch.setattr(
        template_service, "templatize", lambda source: pytest.fail("should not be run")
    )

    convert_upload(3)

    db.expire_all()
    assert db.get(db_models.UserTemplate, 3).latex_content == (
        "Hello {{ personal_info.name }}"
    )


def test_converting_a_template_that_no_longer_exists_is_harmless(db):
    convert_upload(4242)


# --- what an unfinished template may and may not do -----------------------------


@pytest.mark.parametrize("status", [PENDING, FAILED])
def test_an_unfinished_template_is_visible_but_not_selectable(db, status):
    add_template(db, id=5, status=status)

    assert statuses(available_templates(1, db))["user:5"] == status
    with pytest.raises(ValueError, match="not a template"):
        select_template("user:5", 1, db)


@pytest.mark.parametrize("status", [PENDING, FAILED])
def test_an_unfinished_template_never_renders(db, status):
    """It has no LaTeX to render, so generation falls back rather than failing on a
    resume the user is waiting for."""
    add_template(db, id=6, status=status)
    db.add(db_models.TailoringOptions(user_id=1, resume_template="user:6"))
    db.commit()

    assert resolve_template(1, db) == resolve_template()


def test_a_failed_upload_shows_the_user_why(db):
    template = db_models.UserTemplate(
        id=7,
        user_id=1,
        name="Broken",
        status=FAILED,
        error="Undefined control sequence",
    )
    db.add(template)
    db.commit()

    entry = next(t for t in available_templates(1, db) if t["slug"] == "user:7")
    assert entry["error"] == "Undefined control sequence"


def test_builtins_are_always_ready(db):
    gallery = available_templates(1, db)

    assert statuses(gallery)[DEFAULT_TEMPLATE] == READY


# --- deleting one ---------------------------------------------------------------


def test_deleting_a_template_removes_it(db):
    add_template(db, id=8)

    delete_template("user:8", 1, db)

    assert db.get(db_models.UserTemplate, 8) is None


def test_deleting_the_template_in_use_falls_back_to_the_default(db):
    """Otherwise the stored slug points at nothing and the gallery disagrees with
    what a generation would actually use."""
    add_template(db, id=9)
    select_template("user:9", 1, db)

    delete_template("user:9", 1, db)

    options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == 1)
        .one()
    )
    assert options.resume_template == DEFAULT_TEMPLATE


def test_deleting_a_pending_template_is_allowed(db):
    """An upload that is taking too long, or was a mistake, has to be cancellable."""
    add_template(db, id=10, status=PENDING)

    delete_template("user:10", 1, db)

    assert db.get(db_models.UserTemplate, 10) is None


@pytest.mark.parametrize("slug", [DEFAULT_TEMPLATE, "user:999", "nonsense"])
def test_only_the_users_own_templates_can_be_deleted(db, slug):
    with pytest.raises(ValueError, match="not a template"):
        delete_template(slug, 1, db)


def test_another_users_template_cannot_be_deleted(db):
    add_template(db, id=11, user_id=2)

    with pytest.raises(ValueError, match="not a template"):
        delete_template("user:11", 1, db)
    assert db.get(db_models.UserTemplate, 11) is not None
