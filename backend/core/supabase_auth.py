"""Verification of Supabase Auth (GoTrue) access tokens.

Supabase issues JWTs that are either signed with the project's legacy symmetric
secret (HS256) or, on newer projects, with asymmetric signing keys (ES256/RS256)
exposed via the project JWKS endpoint. This module verifies both without an
extra network round-trip per request (the JWKS is fetched once and cached by
``PyJWKClient``).

Uses PyJWT (already a dependency) rather than python-jose so the asymmetric path
and JWKS handling are first-class.
"""

import logging
from functools import lru_cache
from typing import Any, Optional

import jwt
from jwt import PyJWKClient

from backend.config.envs import SUPABASE_JWT_SECRET, SUPABASE_URL

logger = logging.getLogger(__name__)

# Supabase access tokens carry aud="authenticated" for signed-in users.
_AUDIENCE = "authenticated"
# Small leeway (seconds) to tolerate minor clock skew between us and Supabase.
_LEEWAY = 10


def _base_url() -> Optional[str]:
    return SUPABASE_URL.rstrip("/") if SUPABASE_URL else None


def _issuer() -> Optional[str]:
    base = _base_url()
    return f"{base}/auth/v1" if base else None


def _jwks_url() -> Optional[str]:
    base = _base_url()
    return f"{base}/auth/v1/.well-known/jwks.json" if base else None


@lru_cache(maxsize=1)
def _jwk_client() -> PyJWKClient:
    url = _jwks_url()
    if not url:
        raise jwt.PyJWKClientError("SUPABASE_URL is not configured")
    return PyJWKClient(url)


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    """Verify a Supabase access token and return its claims.

    Raises a ``jwt.PyJWTError`` subclass (or ``PyJWKClientError``) if the token
    is missing, malformed, expired, or fails signature/claim verification.
    """
    if not token:
        raise jwt.InvalidTokenError("Empty token")

    header = jwt.get_unverified_header(token)
    alg = header.get("alg", "")
    issuer = _issuer()
    options = {"require": ["exp", "sub"]}

    if alg == "HS256":
        if not SUPABASE_JWT_SECRET:
            raise jwt.InvalidTokenError("SUPABASE_JWT_SECRET is not configured")
        return jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience=_AUDIENCE,
            issuer=issuer,
            leeway=_LEEWAY,
            options=options,
        )

    # Asymmetric signing keys (ES256/RS256) verified via the project JWKS.
    signing_key = _jwk_client().get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256"],
        audience=_AUDIENCE,
        issuer=issuer,
        leeway=_LEEWAY,
        options=options,
    )
