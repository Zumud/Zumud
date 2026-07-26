"""Unit tests for identifier-first auth helpers in backend.api.users."""

import asyncio
from unittest.mock import Mock

import httpx
import pytest
from fastapi import HTTPException, Response, status
from pydantic import SecretStr

from backend.api import users


def _username_record(has_password=True):
    return {
        "email": "[email protected]",
        "has_password": has_password,
        "has_google": False,
    }


class _AsyncClientStub:
    def __init__(self, response=None, error=None, *args, **kwargs):
        self._response = response
        self._error = error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        if self._error is not None:
            raise self._error
        return self._response


def _run_sign_in(payload, monkeypatch, record=None, response=None, error=None):
    monkeypatch.setattr(users, "_username_auth_record", lambda username, _: record)
    monkeypatch.setattr(users, "SUPABASE_URL", "https://unit.supabase.test")
    monkeypatch.setattr(users, "SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.setattr(
        users.httpx,
        "AsyncClient",
        lambda *args, **kwargs: _AsyncClientStub(response=response, error=error),
    )
    api_response = Response()
    result = asyncio.run(users.sign_in_with_username(payload, api_response, db=Mock()))
    return result, api_response


def test_username_auth_record_queries_supabase_user_by_username():
    expected_record = _username_record()
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


def test_check_identifier_rejects_blank_identifier():
    with pytest.raises(HTTPException) as exc_info:
        users.check_identifier(
            users.IdentifierCheckRequest(identifier="   "), db=Mock()
        )

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_check_identifier_for_email_reports_auth_methods(monkeypatch):
    monkeypatch.setattr(
        users, "_email_auth_methods", lambda identifier, _: (True, True, False)
    )

    response = users.check_identifier(
        users.IdentifierCheckRequest(identifier=" Alice@example.com "),
        db=Mock(),
    )

    assert response == {
        "identifier_type": "email",
        "exists": True,
        "has_password": True,
        "has_google": False,
    }


def test_check_identifier_for_email_fails_open_when_lookup_errors(monkeypatch):
    def _boom(identifier, db):
        raise RuntimeError("db offline")

    monkeypatch.setattr(users, "_email_auth_methods", _boom)

    response = users.check_identifier(
        users.IdentifierCheckRequest(identifier="alice@example.com"),
        db=Mock(),
    )

    assert response == {
        "identifier_type": "email",
        "exists": False,
        "has_password": False,
        "has_google": False,
    }


def test_check_identifier_for_username_reports_auth_methods(monkeypatch):
    monkeypatch.setattr(
        users,
        "_username_auth_record",
        lambda username, _: _username_record() if username == "alice" else None,
    )

    response = users.check_identifier(
        users.IdentifierCheckRequest(identifier=" Alice "),
        db=Mock(),
    )

    assert response == {
        "identifier_type": "username",
        "exists": True,
        "has_password": True,
        "has_google": False,
    }


def test_check_identifier_for_username_returns_503_on_lookup_error(monkeypatch):
    def _boom(username, db):
        raise RuntimeError("db offline")

    monkeypatch.setattr(users, "_username_auth_record", _boom)

    with pytest.raises(HTTPException) as exc_info:
        users.check_identifier(
            users.IdentifierCheckRequest(identifier="alice"),
            db=Mock(),
        )

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_sign_in_with_username_rejects_blank_username():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            users.sign_in_with_username(
                users.UsernameSignInRequest(
                    username="   ",
                    password=SecretStr("password123"),
                ),
                Response(),
                db=Mock(),
            )
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_sign_in_with_username_returns_503_when_lookup_fails(monkeypatch):
    def _boom(username, db):
        raise RuntimeError("db offline")

    monkeypatch.setattr(users, "_username_auth_record", _boom)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            users.sign_in_with_username(
                users.UsernameSignInRequest(
                    username="alice",
                    password=SecretStr("password123"),
                ),
                Response(),
                db=Mock(),
            )
        )

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_sign_in_with_username_rejects_missing_auth_record(monkeypatch):
    monkeypatch.setattr(users, "_username_auth_record", lambda username, _: None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            users.sign_in_with_username(
                users.UsernameSignInRequest(
                    username="alice",
                    password=SecretStr("password123"),
                ),
                Response(),
                db=Mock(),
            )
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_sign_in_with_username_requires_supabase_config(monkeypatch):
    monkeypatch.setattr(
        users, "_username_auth_record", lambda username, _: _username_record()
    )
    monkeypatch.setattr(users, "SUPABASE_URL", None)
    monkeypatch.setattr(users, "SUPABASE_PUBLISHABLE_KEY", None)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            users.sign_in_with_username(
                users.UsernameSignInRequest(
                    username="alice",
                    password=SecretStr("password123"),
                ),
                Response(),
                db=Mock(),
            )
        )

    assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


def test_sign_in_with_username_maps_request_error_to_gateway_error(monkeypatch):
    request = httpx.Request("POST", "https://unit.supabase.test/auth/v1/token")
    error = httpx.RequestError("timeout", request=request)

    with pytest.raises(HTTPException) as exc_info:
        _run_sign_in(
            users.UsernameSignInRequest(
                username="alice",
                password=SecretStr("password123"),
            ),
            monkeypatch,
            record=_username_record(),
            error=error,
        )

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY


def test_sign_in_with_username_maps_rate_limit_response(monkeypatch):
    response = httpx.Response(
        status.HTTP_429_TOO_MANY_REQUESTS,
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    with pytest.raises(HTTPException) as exc_info:
        _run_sign_in(
            users.UsernameSignInRequest(
                username="alice",
                password=SecretStr("password123"),
            ),
            monkeypatch,
            record=_username_record(),
            response=response,
        )

    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_sign_in_with_username_maps_supabase_unauthorized_to_gateway_error(monkeypatch):
    auth_response = httpx.Response(
        status.HTTP_401_UNAUTHORIZED,
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    with pytest.raises(HTTPException) as exc_info:
        _run_sign_in(
            users.UsernameSignInRequest(
                username="Alice",
                password=SecretStr("password123"),
            ),
            monkeypatch,
            record=_username_record(),
            response=auth_response,
        )

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY


def test_sign_in_with_username_rejects_other_http_errors_as_invalid_credentials(
    monkeypatch,
):
    response = httpx.Response(
        status.HTTP_400_BAD_REQUEST,
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    with pytest.raises(HTTPException) as exc_info:
        _run_sign_in(
            users.UsernameSignInRequest(
                username="alice",
                password=SecretStr("password123"),
            ),
            monkeypatch,
            record=_username_record(),
            response=response,
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST


def test_sign_in_with_username_rejects_invalid_session_payload(monkeypatch):
    response = httpx.Response(
        status.HTTP_200_OK,
        json={"access_token": "token-without-refresh"},
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    with pytest.raises(HTTPException) as exc_info:
        _run_sign_in(
            users.UsernameSignInRequest(
                username="alice",
                password=SecretStr("password123"),
            ),
            monkeypatch,
            record=_username_record(),
            response=response,
        )

    assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY


def test_sign_in_with_username_returns_session_tokens_and_no_store_headers(monkeypatch):
    response = httpx.Response(
        status.HTTP_200_OK,
        json={"access_token": "access-token", "refresh_token": "refresh-token"},
        request=httpx.Request("POST", "https://unit.supabase.test/auth/v1/token"),
    )

    result, api_response = _run_sign_in(
        users.UsernameSignInRequest(
            username="alice",
            password=SecretStr("password123"),
        ),
        monkeypatch,
        record=_username_record(),
        response=response,
    )

    assert result == {
        "access_token": "access-token",
        "refresh_token": "refresh-token",
    }
    assert api_response.headers["Cache-Control"] == "no-store"
    assert api_response.headers["Pragma"] == "no-cache"
