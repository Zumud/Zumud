"""Fixtures for the integration lane: real API against the local Supabase stack.

Requires the Supabase CLI stack env exported before pytest starts (see
`make test-integration` / the CI integration job). Guarded so it can never
run against a non-local database.
"""

import os
import uuid
from urllib.parse import urlparse

import httpx
import pytest

pytestmark = pytest.mark.integration

_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _database_host() -> str:
    return urlparse(os.environ.get("DATABASE_URL", "")).hostname or ""


@pytest.fixture(scope="session")
def local_stack():
    """Refuse to run unless pointed at a local stack; return its coordinates."""
    if _database_host() not in _LOCAL_HOSTS:
        pytest.skip(
            "integration lane requires the local Supabase stack "
            "(export env via `supabase status -o env`; never point it at prod)"
        )
    return {
        "supabase_url": os.environ["SUPABASE_URL"].rstrip("/"),
        "publishable_key": os.environ["SUPABASE_PUBLISHABLE_KEY"],
        # Admin calls use the legacy service-role JWT, same as `make seed`.
        "service_key": os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ["SUPABASE_SECRET_KEY"],
    }


@pytest.fixture(scope="session")
def app_client(local_stack):
    """TestClient over the real app (import connects to the local DB)."""
    from fastapi.testclient import TestClient

    from backend.main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture()
def supabase_user(local_stack):
    """A fresh confirmed Supabase Auth user + a valid access token."""
    email = f"it-{uuid.uuid4().hex[:12]}@example.com"
    password = "integration-password-1"

    created = httpx.post(
        f"{local_stack['supabase_url']}/auth/v1/admin/users",
        headers={
            "apikey": local_stack["service_key"],
            "Authorization": f"Bearer {local_stack['service_key']}",
        },
        json={"email": email, "password": password, "email_confirm": True},
        timeout=30,
    )
    created.raise_for_status()

    grant = httpx.post(
        f"{local_stack['supabase_url']}/auth/v1/token?grant_type=password",
        headers={"apikey": local_stack["publishable_key"]},
        json={"email": email, "password": password},
        timeout=30,
    )
    grant.raise_for_status()

    return {
        "email": email,
        "access_token": grant.json()["access_token"],
        "auth_id": created.json()["id"],
    }
