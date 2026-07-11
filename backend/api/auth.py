import logging
import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.config.envs import ALGORITHM, SECRET_KEY
from backend.core.supabase_auth import verify_supabase_jwt
from backend.models import db_models
from backend.models.db import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["authentication"])

_WWW_AUTH = {"WWW-Authenticate": "Bearer"}

# Password hashing via pwdlib (maintained passlib replacement; unblocks bcrypt 5).
# Authentication itself is now handled by Supabase Auth; this is kept only so the
# legacy bcrypt hashes in users.password can still be referenced (e.g. by the
# one-time import-into-Supabase script). bcrypt only considers the first 72 bytes
# of a password; bcrypt 5 raises instead of truncating, so we replicate the old
# truncation to keep pre-existing hashes verifiable.
_BCRYPT_MAX_BYTES = 72
_password_hasher = PasswordHash((BcryptHasher(),))


def _bcrypt_input(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


class _PasswordContext:
    """Drop-in replacement for the previous passlib CryptContext (.hash/.verify)."""

    @staticmethod
    def hash(password: str) -> str:
        return _password_hasher.hash(_bcrypt_input(password))

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        try:
            return _password_hasher.verify(_bcrypt_input(password), hashed_password)
        except Exception:
            return False


pwd_context = _PasswordContext()

# Extracts the "Authorization: Bearer <token>" header. tokenUrl is metadata only
# (login is handled by Supabase Auth on the frontend, not a backend endpoint).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=True)


def _generate_unique_username(db: Session, email: str | None) -> str:
    """Derive a unique, filesystem-safe username from the email local part."""
    base = "user"
    if email:
        local = email.split("@", 1)[0]
        cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "", local).strip(".-_").lower()
        if cleaned:
            base = cleaned

    candidate = base
    suffix = 0
    while (
        db.query(db_models.User.id).filter(db_models.User.username == candidate).first()
        is not None
    ):
        suffix += 1
        candidate = f"{base}{suffix}"
    return candidate


def _provision_user(db: Session, sub: str, email: str | None) -> db_models.User:
    """Create a new profile row (+ empty resume) for a first-time Supabase user."""
    for _ in range(3):
        username = _generate_unique_username(db, email)
        user = db_models.User(
            username=username,
            email=email,
            supabase_uid=sub,
            password=None,
        )
        db.add(user)
        try:
            db.flush()
            # Mirror the legacy signup flow: every user owns an (initially empty)
            # resume row that the rest of the app assumes exists.
            db.add(
                db_models.Resume(
                    user_id=user.id,
                    resume_content="",
                    resume_file_path=None,
                )
            )
            db.commit()
            db.refresh(user)
            logger.info(
                "Provisioned profile for Supabase user %s (username=%s)", sub, username
            )
            return user
        except IntegrityError:
            db.rollback()
            # A concurrent request may have created the row, or the username
            # clashed; re-check by the stable supabase_uid before retrying.
            existing = (
                db.query(db_models.User)
                .filter(db_models.User.supabase_uid == sub)
                .first()
            )
            if existing is not None:
                return existing

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not provision user account.",
        headers=_WWW_AUTH,
    )


def _get_or_create_user_from_claims(claims: dict, db: Session) -> db_models.User:
    """Map verified Supabase JWT claims to a local user, creating one if needed."""
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token (missing subject).",
            headers=_WWW_AUTH,
        )

    raw_email = claims.get("email")
    email = (
        raw_email.strip().lower()
        if isinstance(raw_email, str) and raw_email.strip()
        else None
    )

    user = db.query(db_models.User).filter(db_models.User.supabase_uid == sub).first()
    if user is not None:
        if email and not user.email:
            user.email = email
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
        return user

    # Adopt an existing (e.g. bulk-imported or pre-migration) row by verified
    # email when it has not yet been linked to a Supabase identity.
    if email:
        existing = (
            db.query(db_models.User)
            .filter(func.lower(db_models.User.email) == email)
            .first()
        )
        if existing is not None:
            if existing.supabase_uid is None:
                existing.supabase_uid = sub
                try:
                    db.commit()
                    return existing
                except IntegrityError:
                    db.rollback()
                    relinked = (
                        db.query(db_models.User)
                        .filter(db_models.User.supabase_uid == sub)
                        .first()
                    )
                    if relinked is not None:
                        return relinked
            elif str(existing.supabase_uid) == str(sub):
                return existing
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This email is already associated with another account.",
                    headers=_WWW_AUTH,
                )

    return _provision_user(db, sub, email)


def _user_from_legacy_token(token: str, db: Session) -> db_models.User | None:
    """Transitional fallback: accept pre-migration app-issued HS256 tokens.

    Lets users holding an unexpired legacy session stay logged in across the
    cutover. Remove this (and SECRET_KEY/ALGORITHM auth usage) after the window.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    uid = payload.get("user_id")
    if uid is None:
        return None
    try:
        uid = int(uid)
    except (TypeError, ValueError):
        return None

    return db.query(db_models.User).filter(db_models.User.id == uid).first()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Resolve the current user from a Supabase access token (legacy token as fallback)."""
    claims = None
    try:
        claims = verify_supabase_jwt(token)
    except Exception:
        claims = None

    if claims is not None:
        return _get_or_create_user_from_claims(claims, db)

    legacy_user = _user_from_legacy_token(token, db)
    if legacy_user is not None:
        return legacy_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your session has expired. Please log in again to continue.",
        headers=_WWW_AUTH,
    )


@router.post("/logout")
def logout():
    # Sessions are stateless (Supabase access tokens); the frontend clears its
    # Supabase session via supabase.auth.signOut(). Kept for backwards compat.
    return {"message": "Logged out successfully"}
