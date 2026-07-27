import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api import users
from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.models import db_models
from backend.models.db import Base, get_db


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        db.add_all(
            [
                db_models.User(id=1, username="user-one", email="one@example.com"),
                db_models.User(id=2, username="user-two", email="two@example.com"),
            ]
        )
        db.commit()
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    app = FastAPI()
    app.include_router(users.router)

    def override_get_db():
        yield db_session

    def override_current_user():
        return SimpleNamespace(id=1, username="user-one", email="one@example.com")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user
    return TestClient(app)


def test_user_can_create_ai_rule(client):
    response = client.post(
        "/users/me/ai-rules",
        json={"title": "Length", "instruction": "Keep my resume under two pages."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Length"
    assert body["instruction"] == "Keep my resume under two pages."
    assert body["is_enabled"] is True
    assert "priority" not in body


def test_new_ai_rules_are_enabled_by_default_even_if_client_sends_disabled(client):
    response = client.post(
        "/users/me/ai-rules",
        json={
            "title": "Language",
            "instruction": "Always generate documents in English.",
            "is_enabled": False,
        },
    )

    assert response.status_code == 201
    assert response.json()["is_enabled"] is True


def test_user_can_edit_and_delete_own_ai_rule(client):
    created = client.post(
        "/users/me/ai-rules",
        json={"instruction": "Use concise bullet points."},
    ).json()

    updated = client.put(
        f"/users/me/ai-rules/{created['id']}",
        json={"title": "Tone", "instruction": "Use concise, specific bullets."},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Tone"
    assert updated.json()["instruction"] == "Use concise, specific bullets."

    deleted = client.delete(f"/users/me/ai-rules/{created['id']}")
    assert deleted.status_code == 204
    assert client.get("/users/me/ai-rules").json() == []


def test_user_can_update_only_ai_rule_title(client):
    created = client.post(
        "/users/me/ai-rules",
        json={"instruction": "Use concise bullet points."},
    ).json()

    updated = client.put(
        f"/users/me/ai-rules/{created['id']}",
        json={"title": "Tone"},
    )

    assert updated.status_code == 200
    assert updated.json()["title"] == "Tone"
    assert updated.json()["instruction"] == "Use concise bullet points."
    assert updated.json()["is_enabled"] is True


def test_ai_rule_update_rejects_null_instruction(client):
    created = client.post(
        "/users/me/ai-rules",
        json={"instruction": "Use concise bullet points."},
    ).json()

    response = client.put(
        f"/users/me/ai-rules/{created['id']}",
        json={"instruction": None},
    )

    assert response.status_code == 422


def test_ai_rule_update_rejects_null_is_enabled(client):
    created = client.post(
        "/users/me/ai-rules",
        json={"instruction": "Use concise bullet points."},
    ).json()

    response = client.put(
        f"/users/me/ai-rules/{created['id']}",
        json={"is_enabled": None},
    )

    assert response.status_code == 422


def test_user_cannot_access_another_users_ai_rules(client, db_session):
    other_rule = db_models.UserAIRule(
        user_id=2,
        title="Other",
        instruction="Always write in French.",
    )
    db_session.add(other_rule)
    db_session.commit()
    db_session.refresh(other_rule)

    assert client.get("/users/me/ai-rules").json() == []
    update_response = client.put(
        f"/users/me/ai-rules/{other_rule.id}",
        json={"instruction": "Always write in English."},
    )
    delete_response = client.delete(f"/users/me/ai-rules/{other_rule.id}")

    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_empty_ai_rule_instruction_is_rejected(client):
    response = client.post("/users/me/ai-rules", json={"instruction": "   "})

    assert response.status_code == 422


def test_ai_rule_instruction_with_exactly_500_characters_is_accepted(client):
    response = client.post("/users/me/ai-rules", json={"instruction": "a" * 500})

    assert response.status_code == 201
    assert response.json()["instruction"] == "a" * 500


def test_ai_rule_instruction_longer_than_500_characters_is_rejected(client):
    response = client.post("/users/me/ai-rules", json={"instruction": "a" * 501})

    assert response.status_code == 422


def test_unauthenticated_ai_rule_requests_are_rejected(db_session):
    app = FastAPI()
    app.include_router(users.router)

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    unauthenticated_client = TestClient(app)

    response = unauthenticated_client.get("/users/me/ai-rules")

    assert response.status_code == 401


def test_priority_and_reorder_endpoint_no_longer_exist(client):
    created = client.post(
        "/users/me/ai-rules",
        json={
            "instruction": "Use concise bullet points.",
            "priority": 500,
        },
    ).json()

    assert "priority" not in created

    response = client.put(
        "/users/me/ai-rules/order",
        json={"rules": [{"id": created["id"], "priority": 0}]},
    )
    assert response.status_code == 422


def test_enabled_rules_are_prompted_equally_and_disabled_rules_are_excluded(db_session):
    db_session.add_all(
        [
            db_models.UserAIRule(
                user_id=1,
                title="Direct",
                instruction="Do not copy job-description skills verbatim.",
                is_enabled=True,
            ),
            db_models.UserAIRule(
                user_id=1,
                title="Length",
                instruction="Keep my resume under two pages.",
                is_enabled=True,
            ),
            db_models.UserAIRule(
                user_id=1,
                title="Disabled",
                instruction="Write everything in French.",
                is_enabled=False,
            ),
        ]
    )
    db_session.commit()

    prompt = ai_service.format_ai_rules_for_prompt(
        ai_service.get_enabled_ai_rules(1, db_session)
    )

    assert "- Length: Keep my resume under two pages." in prompt
    assert "- Direct: Do not copy job-description skills verbatim." in prompt
    assert "Write everything in French." not in prompt
    assert "No rule is more important because of its position" in prompt
    assert "do not choose between them based on ordering" in prompt
    assert "priority" not in prompt.lower()
    assert "earlier numbered rule" not in prompt


class _FakeParsedMessage:
    def __init__(self, content: str):
        self.content = content


class _FakeChoice:
    def __init__(self, content: str):
        self.message = _FakeParsedMessage(content)


class _FakeParsedResponse:
    def __init__(self, content: str):
        self.choices = [_FakeChoice(content)]


class _FakeAsyncCompletions:
    def __init__(self, captured):
        self.captured = captured

    async def parse(self, **kwargs):
        self.captured.append(kwargs)
        return _FakeParsedResponse(
            json.dumps({"personal_info": {"name": "Ada Lovelace"}})
        )


class _FakeSyncCompletions:
    def __init__(self, captured):
        self.captured = captured

    def parse(self, **kwargs):
        self.captured.append(kwargs)
        return _FakeParsedResponse(
            json.dumps({"personal_info": {"name": "Ada Lovelace"}})
        )


def test_user_rules_are_applied_to_resume_generation(monkeypatch, tmp_path):
    captured = []
    fake_completions = _FakeAsyncCompletions(captured)
    monkeypatch.setattr(
        ai_service,
        "async_client",
        SimpleNamespace(
            beta=SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))
        ),
    )
    monkeypatch.setattr(
        ai_service,
        "generate_pdf_from_latex",
        lambda *_args, **_kwargs: SimpleNamespace(content=b"%PDF"),
    )

    asyncio.run(
        ai_service.generate_structured_latex_resume_async(
            str(tmp_path),
            "Resume text",
            "Job description",
            ai_rules_prompt=ai_service.format_ai_rules_for_prompt(
                [
                    SimpleNamespace(
                        title="Length",
                        instruction="Keep my resume under two pages.",
                    )
                ]
            ),
        )
    )

    prompt = captured[0]["messages"][1]["content"]
    assert "USER-SPECIFIC AI RULES" in prompt
    assert "Keep my resume under two pages." in prompt


def test_user_rules_are_applied_to_resume_editing(monkeypatch, tmp_path):
    captured = []
    fake_completions = _FakeSyncCompletions(captured)
    monkeypatch.setattr(
        ai_service,
        "client",
        SimpleNamespace(
            beta=SimpleNamespace(chat=SimpleNamespace(completions=fake_completions))
        ),
    )
    monkeypatch.setattr(
        ai_service,
        "generate_pdf_from_latex",
        lambda *_args, **_kwargs: SimpleNamespace(content=b"%PDF"),
    )

    ai_service.update_resume_with_instructions(
        json.dumps({"personal_info": {"name": "Ada Lovelace"}}),
        "Job description",
        "Make the summary stronger.",
        str(tmp_path),
        ai_rules_prompt=ai_service.format_ai_rules_for_prompt(
            [
                SimpleNamespace(
                    title="Language",
                    instruction="Always generate my resume in English.",
                )
            ]
        ),
    )

    prompt = captured[0]["messages"][1]["content"]
    assert "USER-SPECIFIC AI RULES" in prompt
    assert "Always generate my resume in English." in prompt


def test_profile_creation_form_has_no_enabled_or_priority_controls():
    profile_source = Path(
        "frontend/src/components/profile/profile-settings-page.tsx"
    ).read_text()
    api_source = Path("frontend/src/lib/api.ts").read_text()

    assert 'type="checkbox"' not in profile_source
    assert "isEnabled" not in profile_source
    assert "ArrowUp" not in profile_source
    assert "ArrowDown" not in profile_source
    assert "Priority" not in profile_source
    assert "priority" not in api_source
    assert "reorder" not in api_source


def test_profile_rules_use_compact_rows_and_disabled_visual_state():
    profile_source = Path(
        "frontend/src/components/profile/profile-settings-page.tsx"
    ).read_text()

    assert "setSelectedRule(rule)" in profile_source
    assert "line-through" in profile_source
    assert "rule.instruction}</p>" not in profile_source
    assert "Created" in profile_source
    assert "Last updated" in profile_source
    assert "selectedRule.instruction" in profile_source


def test_profile_row_actions_stop_details_modal_from_opening():
    profile_source = Path(
        "frontend/src/components/profile/profile-settings-page.tsx"
    ).read_text()

    assert "stopRowAction" in profile_source
    assert "event.stopPropagation()" in profile_source
    assert "handleToggleRule(rule)" in profile_source
    assert "startEditingRule(rule)" in profile_source
    assert "setDeleteTarget(rule)" in profile_source
