"""Helpers shared by the applications routers.

These factor out the four blocks that used to be copy-pasted into every
endpoint: resume checks, preferences lookup, non-blocking billing, and the
"dual storage" cloud mirror.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.core.storage_service import safe_upload_with_fallback
from backend.core.stripe_billing_service import process_billing_event
from backend.models import db_models
from backend.utils.path_ops import get_current_session_info

logger = logging.getLogger(__name__)


def require_resume_record(current_user) -> None:
    """404 unless the user has a resume row (download endpoints)."""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a resume"
        )


def require_resume_content(current_user, before: str = "first") -> None:
    """404/400 unless the user has a resume with content (generation endpoints).

    `before` finishes the 400 message: "... add your resume details {before}."
    """
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume record. Please upload a resume first.",
        )
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No resume content found. Please add your resume details {before}.",
        )


def get_preferences_text(db: Session, user_id: int) -> str | None:
    """The user's stored preferences text, if any."""
    preferences = (
        db.query(db_models.UserPreferences)
        .filter(db_models.UserPreferences.user_id == user_id)
        .first()
    )
    return preferences.preferences_text if preferences else None


def bill_safely(event: str, current_user) -> None:
    """Stripe metered billing (non-blocking; logs on failure)."""
    try:
        process_billing_event(
            event, email=current_user.email, name=current_user.username
        )
    except Exception as e:
        logger.error(f"Stripe billing flow failed for {event}: {e}")


def upload_to_cloud(
    username: str, label: str, upload_fn, user_id, company_name, *contents
) -> None:
    """DUAL STORAGE: mirror generated files to Supabase cloud storage.

    Runs after local storage succeeds and never affects the API response.
    Skipped when the user has no active application session.
    """
    try:
        session_info = get_current_session_info(username)
        if session_info:
            session_id, _ = session_info
            safe_upload_with_fallback(
                upload_fn, user_id, session_id, company_name, *contents
            )
    except Exception as e:
        logger.error(f"Cloud storage upload failed for {label}: {e}")
