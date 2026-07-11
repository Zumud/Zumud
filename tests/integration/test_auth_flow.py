"""End-to-end auth contract through the real API and Supabase Auth (GoTrue).

Exercises the invariants that the unit lane can only approximate: a real
GoTrue-issued token is accepted, the profile (+ empty resume) is lazily
provisioned exactly once, and bad tokens never get through.
"""

from unittest.mock import AsyncMock, patch

import pytest

pytestmark = pytest.mark.integration


def auth_header(user):
    return {"Authorization": f"Bearer {user['access_token']}"}


def test_health_endpoint(app_client):
    response = app_client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_unauthenticated_request_rejected(app_client):
    assert app_client.get("/users/me").status_code == 401


def test_garbage_token_rejected(app_client):
    response = app_client.get(
        "/users/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_first_request_lazily_provisions_profile_and_resume(app_client, supabase_user):
    me = app_client.get("/users/me", headers=auth_header(supabase_user))
    assert me.status_code == 200
    profile = me.json()
    assert profile["email"] == supabase_user["email"]
    # Username is derived from the email local part (filesystem-safe).
    assert profile["username"].startswith("it-")

    # The empty resume row every feature assumes exists.
    resume = app_client.get("/users/me/resume", headers=auth_header(supabase_user))
    assert resume.status_code == 200
    assert resume.json()["resume_content"] == ""


def test_provisioning_is_idempotent(app_client, supabase_user):
    first = app_client.get("/users/me", headers=auth_header(supabase_user)).json()
    second = app_client.get("/users/me", headers=auth_header(supabase_user)).json()
    assert first["id"] == second["id"]
    assert first["username"] == second["username"]


def test_resume_update_roundtrip(app_client, supabase_user):
    content = "Jane Doe\nSenior Platform Engineer\n10 years of Python."
    # Background AI formatting is out of scope here (real-AI lane covers it).
    with patch(
        "backend.api.users.format_resume_text", new=AsyncMock(return_value=content)
    ):
        put = app_client.put(
            "/users/me/resume",
            json={"resume_content": content},
            headers=auth_header(supabase_user),
        )
    assert put.status_code == 200

    got = app_client.get("/users/me/resume", headers=auth_header(supabase_user))
    assert got.json()["resume_content"] == content


def test_check_email_reports_signin_methods(app_client, supabase_user):
    # Provision first so both auth.users and public.users rows exist.
    app_client.get("/users/me", headers=auth_header(supabase_user))

    known = app_client.post(
        "/users/check-email", json={"email": supabase_user["email"]}
    ).json()
    assert known == {"exists": True, "has_password": True, "has_google": False}

    unknown = app_client.post(
        "/users/check-email", json={"email": "nobody-here@example.com"}
    ).json()
    assert unknown["exists"] is False
