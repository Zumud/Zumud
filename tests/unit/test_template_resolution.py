"""Which template a generation renders with.

Selection is one slug on `tailoring_options.resume_template`. The behaviour that
matters most here is the fallback: a stale or unresolvable preference must degrade
to the default built-in rather than fail a generation the user is waiting on.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.template_service import resolve_template, selected_slug
from backend.models import db_models
from backend.models.db import Base
from backend.models.templates import DEFAULT_TEMPLATE, builtin_template

DEFAULT_SOURCE = builtin_template("mteck")["structure"]


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        session.add_all(
            [
                db_models.User(id=1, username="user-one", email="one@example.com"),
                db_models.User(id=2, username="user-two", email="two@example.com"),
            ]
        )
        session.commit()
        yield session
    finally:
        session.close()


def add_template(db, *, id, user_id, latex="Hello {{ personal_info.name }}"):
    db.add(
        db_models.UserTemplate(
            id=id,
            user_id=user_id,
            name=f"template-{id}",
            latex_content=latex,
            compiler="xelatex",
        )
    )
    db.commit()


def select(db, user_id, slug):
    db.add(db_models.TailoringOptions(user_id=user_id, resume_template=slug))
    db.commit()


def test_user_without_preferences_gets_the_default(db):
    assert selected_slug(1, db) == DEFAULT_TEMPLATE
    assert resolve_template(1, db)["structure"] == DEFAULT_SOURCE


def test_anonymous_generation_gets_the_default(db):
    assert resolve_template(None, None)["structure"] == DEFAULT_SOURCE


def test_selected_builtin_is_used(db):
    select(db, 1, "builtin:mteck")

    assert resolve_template(1, db)["structure"] == DEFAULT_SOURCE


def test_selected_user_template_is_used(db):
    add_template(db, id=7, user_id=1)
    select(db, 1, "user:7")

    resolved = resolve_template(1, db)

    assert resolved["structure"] == "Hello {{ personal_info.name }}"
    assert resolved["compiler"] == "xelatex"


def test_another_users_template_is_never_resolved(db):
    """A slug is just a string, so ownership is enforced at lookup."""
    add_template(db, id=8, user_id=2, latex="secret")
    select(db, 1, "user:8")

    assert resolve_template(1, db)["structure"] == DEFAULT_SOURCE


@pytest.mark.parametrize(
    "slug",
    [
        "user:999",  # deleted template
        "user:not-a-number",  # corrupted slug
        "builtin:retired-template",  # built-in removed from the registry
        "nonsense",  # unprefixed junk
    ],
)
def test_unresolvable_selection_falls_back_to_the_default(db, slug):
    select(db, 1, slug)

    assert resolve_template(1, db)["structure"] == DEFAULT_SOURCE
