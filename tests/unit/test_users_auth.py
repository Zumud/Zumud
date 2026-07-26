"""Unit tests for identifier-first auth helpers in backend.api.users."""

import asyncio
from unittest.mock import Mock

import httpx
import pytest
from fastapi import HTTPException, Response, status
from pydantic import SecretStr

from backend.api import users


def test_username_auth_record_queries_supabase_user_by_username():
    expected_record = {
        "email": "[email protected]",
        "has_password": True,
        "has_google": False,
    }
    mappings_result = Mock()
    mappings_result.first.return_value = expected_record
    execute_result = Mock()
    execute_result.mappings.return_value = mappings_result
    db = Mock()
    db.execute.return_value = execute_result

    record = users._username_auth_record("alice", db)

    assert record == expected_record
    db.execute.assert_called_once()
    statement = db.execute.call_args.args[0]
    params = db.execute.call_args.args[1]
    assert "FROM public.users pu" in str(statement)
    assert "WHERE lower(pu.username) = :username" in str(statement)
    assert params == {"username": "alice"}


def test_check_identifier_for_username_reports_auth_methods(monkeypatch):
    db = Mock()
    monkeypatch.setattr(
        users,
        "_username_auth_record",
        lambda username, _: (
            {
                "email": "[email protected]",
                "has_password": True,
                "has_google": False,
            }
            if username == "alice"
            else None
        ),
    )

    response = users.check_identifier(
        users.IdentifierCheckRequest(identifier=" Alice "), db=db
    )

    assert response == {
        "identifier_type": "username",
        "exists": True,
        "has_password": True,
        "has_google": False,
    }


def test_sign_in_with_username_maps_supabase_unauthorized_to_gateway_error(monkeypatch):
    monkeypatch.setattr(
        users,
        "_username_auth_record",
        lambda username, _: {
            "email": "[email protected]",
            "has_password": True,
            "has_google": False,
        },
    )
    monkeypatch.setattr(users, "SUPABASE_URL", "https://unit.supabase.test")
    monkeypatch.setattr(users, "SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")

    auth_response = httpx.Response(
        status.HTTP_401_UNAUTHORIZED,
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    class _AsyncClientStub:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            return auth_response

    monkeypatch.setattr(users.httpx, "AsyncClient", _AsyncClientStub)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            users.sign_in_with_username(
                users.UsernameSignInRequest(
                    username="Alice", password=SecretStr("password123")
                ),
                Response(),
                db=Mock(),
            )
        )

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
    assert (
        exc_info.value.detail == "Sign-in is temporarily unavailable. Please try again."
    )
