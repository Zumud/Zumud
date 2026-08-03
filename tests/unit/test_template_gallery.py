"""Listing the templates a user may pick, and recording the one they picked.

The gallery is the only place a user ever sees the slug vocabulary, so what matters
is that built-ins and a user's own templates arrive as one list, that exactly one
entry is ever marked selected, and that choosing a template changes nothing else
about how their resumes are generated.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.template_service import available_templates, select_template
from backend.models import db_models
from backend.models.db import Base
from backend.models.tailoring_options import TailoringOptionsBase
from backend.models.templates import BUILTINS, DEFAULT_TEMPLATE


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


def add_template(db, *, id, user_id, name="My template"):
    db.add(
        db_models.UserTemplate(
            id=id,
            user_id=user_id,
            name=name,
            latex_content="Hello {{ personal_info.name }}",
            compiler="pdflatex",
        )
    )
    db.commit()


def selected(gallery):
    return [template["slug"] for template in gallery if template["selected"]]


def test_every_builtin_is_offered(db):
    gallery = available_templates(1, db)

    assert [template["slug"] for template in gallery] == [
        f"builtin:{slug}" for slug in BUILTINS
    ]
    assert all(template["description"] for template in gallery)


def test_a_builtin_carries_its_committed_thumbnail(db):
    gallery = available_templates(1, db)

    assert gallery[0]["preview_url"] == "/templates/mteck.png"


def test_a_users_own_templates_are_offered_after_the_builtins(db):
    add_template(db, id=4, user_id=1, name="Mine")

    gallery = available_templates(1, db)

    assert gallery[-1]["slug"] == "user:4"
    assert gallery[-1]["name"] == "Mine"
    # No thumbnail until an upload is verified, rather than a broken image.
    assert gallery[-1]["preview_url"] is None


def test_another_users_templates_are_not_offered(db):
    add_template(db, id=5, user_id=2, name="Theirs")

    assert "user:5" not in [template["slug"] for template in available_templates(1, db)]


def test_the_default_is_marked_selected_before_any_choice(db):
    assert selected(available_templates(1, db)) == [DEFAULT_TEMPLATE]


def test_choosing_a_template_marks_exactly_it(db):
    add_template(db, id=6, user_id=1)

    select_template("user:6", 1, db)

    assert selected(available_templates(1, db)) == ["user:6"]


def test_an_unresolvable_choice_still_shows_the_default_as_selected(db):
    """The slug renders as the default, so the gallery has to agree with what a
    generation would actually use rather than showing nothing selected."""
    db.add(db_models.TailoringOptions(user_id=1, resume_template="user:999"))
    db.commit()

    assert selected(available_templates(1, db)) == [DEFAULT_TEMPLATE]


@pytest.mark.parametrize(
    "slug",
    [
        "builtin:not-a-template",
        "user:999",
        "nonsense",
    ],
)
def test_a_template_that_is_not_the_users_cannot_be_selected(db, slug):
    with pytest.raises(ValueError, match="not a template"):
        select_template(slug, 1, db)


def test_another_users_template_cannot_be_selected(db):
    add_template(db, id=7, user_id=2)

    with pytest.raises(ValueError, match="not a template"):
        select_template("user:7", 1, db)


def test_choosing_a_template_does_not_change_the_ai_model(db):
    """Creating the options row is a side effect of picking a template, and the
    column default is a cheaper model than a user with no row actually runs on — so
    this would otherwise downgrade every generation they make afterwards."""
    select_template(DEFAULT_TEMPLATE, 1, db)

    options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == 1)
        .one()
    )
    assert options.ai_model == TailoringOptionsBase().ai_model


def test_choosing_again_updates_the_existing_row(db):
    add_template(db, id=8, user_id=1)

    select_template("user:8", 1, db)
    select_template(DEFAULT_TEMPLATE, 1, db)

    rows = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == 1)
        .all()
    )
    assert len(rows) == 1
    assert rows[0].resume_template == DEFAULT_TEMPLATE
