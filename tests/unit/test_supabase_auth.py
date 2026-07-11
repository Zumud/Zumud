"""Contract tests for Supabase access-token verification.

These pin the security-critical behavior of backend.core.supabase_auth:
valid tokens (HS256 and ES256/JWKS) yield claims; expired, tampered,
mis-audienced, mis-issued, or unverifiable tokens are always rejected.
"""

import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from backend.core import supabase_auth

SECRET = "unit-test-jwt-secret-0123456789abcdef"
SUPABASE_URL = "https://unit.supabase.test"
ISSUER = f"{SUPABASE_URL}/auth/v1"


def make_claims(**overrides):
    claims = {
        "sub": "00000000-0000-0000-0000-000000000001",
        "email": "user@example.com",
        "aud": "authenticated",
        "iss": ISSUER,
        "exp": int(time.time()) + 3600,
    }
    claims.update(overrides)
    return {k: v for k, v in claims.items() if v is not None}


def hs256_token(**overrides) -> str:
    return jwt.encode(make_claims(**overrides), SECRET, algorithm="HS256")


@pytest.fixture(autouse=True)
def configured_env(monkeypatch):
    monkeypatch.setattr(supabase_auth, "SUPABASE_JWT_SECRET", SECRET)
    monkeypatch.setattr(supabase_auth, "SUPABASE_URL", SUPABASE_URL)
    # Drop any JWKS client cached under a different SUPABASE_URL. ES256 tests
    # replace _jwk_client with a stub, hence the hasattr guard.
    if hasattr(supabase_auth._jwk_client, "cache_clear"):
        supabase_auth._jwk_client.cache_clear()


class TestHS256:
    def test_valid_token_returns_claims(self):
        claims = supabase_auth.verify_supabase_jwt(hs256_token())
        assert claims["sub"] == "00000000-0000-0000-0000-000000000001"
        assert claims["email"] == "user@example.com"

    def test_expired_token_rejected(self):
        token = hs256_token(exp=int(time.time()) - 120)
        with pytest.raises(jwt.ExpiredSignatureError):
            supabase_auth.verify_supabase_jwt(token)

    def test_wrong_audience_rejected(self):
        with pytest.raises(jwt.InvalidAudienceError):
            supabase_auth.verify_supabase_jwt(hs256_token(aud="anon"))

    def test_wrong_issuer_rejected(self):
        token = hs256_token(iss="https://attacker.example/auth/v1")
        with pytest.raises(jwt.InvalidIssuerError):
            supabase_auth.verify_supabase_jwt(token)

    def test_missing_sub_rejected(self):
        with pytest.raises(jwt.MissingRequiredClaimError):
            supabase_auth.verify_supabase_jwt(hs256_token(sub=None))

    def test_tampered_signature_rejected(self):
        forged = jwt.encode(
            make_claims(), "wrong-secret-0123456789abcdefghij", algorithm="HS256"
        )
        with pytest.raises(jwt.InvalidSignatureError):
            supabase_auth.verify_supabase_jwt(forged)

    def test_empty_token_rejected(self):
        with pytest.raises(jwt.InvalidTokenError):
            supabase_auth.verify_supabase_jwt("")

    def test_hs256_without_configured_secret_rejected(self, monkeypatch):
        monkeypatch.setattr(supabase_auth, "SUPABASE_JWT_SECRET", None)
        with pytest.raises(jwt.InvalidTokenError):
            supabase_auth.verify_supabase_jwt(hs256_token())


class _StubSigningKey:
    def __init__(self, key):
        self.key = key


class _StubJWKClient:
    """Stands in for PyJWKClient so no JWKS endpoint is fetched."""

    def __init__(self, public_key):
        self._public_key = public_key

    def get_signing_key_from_jwt(self, token):
        return _StubSigningKey(self._public_key)


class TestES256:
    """The path production uses (Supabase asymmetric signing keys via JWKS)."""

    @pytest.fixture(autouse=True)
    def es256_keys(self, monkeypatch):
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        monkeypatch.setattr(
            supabase_auth,
            "_jwk_client",
            lambda: _StubJWKClient(self.private_key.public_key()),
        )

    def es256_token(self, **overrides) -> str:
        return jwt.encode(make_claims(**overrides), self.private_key, algorithm="ES256")

    def test_valid_token_returns_claims(self):
        claims = supabase_auth.verify_supabase_jwt(self.es256_token())
        assert claims["sub"] == "00000000-0000-0000-0000-000000000001"

    def test_expired_token_rejected(self):
        token = self.es256_token(exp=int(time.time()) - 120)
        with pytest.raises(jwt.ExpiredSignatureError):
            supabase_auth.verify_supabase_jwt(token)

    def test_token_signed_by_other_key_rejected(self):
        other_key = ec.generate_private_key(ec.SECP256R1())
        forged = jwt.encode(make_claims(), other_key, algorithm="ES256")
        with pytest.raises(jwt.InvalidSignatureError):
            supabase_auth.verify_supabase_jwt(forged)
