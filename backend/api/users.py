import base64
import logging
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.core.ai_service import format_user_preferences
from backend.core.storage_service import safe_upload_with_fallback, storage_service
from backend.models import db_models
from backend.models.db import SessionLocal, get_db
from backend.models.legal_authorization_models import LegalAuthorization
from backend.models.resume_models import Resume, ResumeBase
from backend.models.tailoring_options import TailoringOptions, TailoringOptionsBase
from backend.models.user_models import User, UserPreference, UserPreferenceCreate
from backend.utils.file_ops import extract_text_from_pdf
from backend.utils.file_utils import save_base64_pdf
from backend.utils.resume_formatter import format_resume_text

router = APIRouter(prefix="/users", tags=["users"])

logger = logging.getLogger(__name__)


@router.get("/me", response_model=User)
def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user information"""
    return current_user


class EmailCheckRequest(BaseModel):
    email: EmailStr


@router.post("/check-email")
def check_email(payload: EmailCheckRequest, db: Session = Depends(get_db)):
    """Report which sign-in methods exist for an email (identifier-first auth UI).

    Public endpoint. It intentionally reveals whether an email is registered —
    inherent to identifier-first flows (Stripe/Google-style) and an accepted
    trade-off. Reads Supabase Auth (auth.users / auth.identities), the source of
    truth for login.
    """
    email = payload.email.strip().lower()
    try:
        row = db.execute(
            text(
                """
                SELECT
                  EXISTS (SELECT 1 FROM auth.users WHERE lower(email) = :email) AS does_exist,
                  EXISTS (SELECT 1 FROM auth.users
                          WHERE lower(email) = :email
                            AND encrypted_password IS NOT NULL
                            AND encrypted_password <> '') AS has_password,
                  EXISTS (SELECT 1 FROM auth.identities i
                          JOIN auth.users u ON u.id = i.user_id
                          WHERE lower(u.email) = :email AND i.provider = 'google') AS has_google
                """
            ),
            {"email": email},
        ).first()
    except Exception as e:
        # Fail safe: never block the UI if the auth-schema read fails.
        logger.error(f"check-email lookup failed: {e}")
        return {"exists": False, "has_password": False, "has_google": False}

    return {
        "exists": bool(row[0]),
        "has_password": bool(row[1]),
        "has_google": bool(row[2]),
    }


async def process_resume_background(
    user_id: int,
    resume_content: str,
):
    """Background task to process resume content and update the database"""
    # Create a new session for this background task
    db = SessionLocal()
    try:
        # Format resume content if it exists and isn't empty
        if resume_content and resume_content.strip():
            # Use the async format_resume_text function
            formatted_content = await format_resume_text(resume_content)

            # Update the resume record with formatted content
            db_resume = (
                db.query(db_models.Resume)
                .filter(db_models.Resume.user_id == user_id)
                .first()
            )
            if db_resume:
                db_resume.resume_content = formatted_content
                db.commit()
    except Exception as e:
        logger.error(f"Error in background resume processing: {e}")
    finally:
        db.close()


# Account creation is handled by Supabase Auth on the frontend (email/password
# or "Continue with Google"). The local profile row and its empty resume are
# created lazily on first authenticated request (see auth.get_current_user), and
# an initial resume is attached afterwards via POST /users/me/resume/upload.


@router.get("/me/resume", response_model=Resume)
def get_user_resume(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's resume"""
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload or create a resume to get started.",
        )
    return resume


@router.put("/me/resume", response_model=Resume)
def update_resume(
    resume_data: ResumeBase,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """Update current user's resume"""

    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload or create a resume first.",
        )

    # Get the updated content
    resume_content = resume_data.resume_content

    # Store unformatted content initially
    resume.resume_content = resume_content
    resume.last_updated = datetime.now(timezone.utc)

    db.commit()

    # Format the resume content in the background
    background_tasks.add_task(
        process_resume_background,
        current_user.id,
        resume_content,
    )

    return resume


@router.get("/me/work-authorization", response_model=LegalAuthorization)
def get_work_authorization(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's work authorization information"""
    legal_auth = (
        db.query(db_models.LegalAuthorization)
        .filter(db_models.LegalAuthorization.user_id == current_user.id)
        .first()
    )
    if not legal_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} does not have work authorization information",
        )
    return legal_auth


@router.put("/me/work-authorization", response_model=LegalAuthorization)
def update_work_authorization(
    work_authorization: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's work authorization information"""
    legal_auth = (
        db.query(db_models.LegalAuthorization)
        .filter(db_models.LegalAuthorization.user_id == current_user.id)
        .first()
    )

    if legal_auth:
        legal_auth.work_authorization = work_authorization
        legal_auth.last_updated = datetime.now(timezone.utc)
    else:
        legal_auth = db_models.LegalAuthorization(
            user_id=current_user.id, work_authorization=work_authorization
        )
        db.add(legal_auth)

    db.commit()
    db.refresh(legal_auth)
    return legal_auth


@router.get("/me/tailoring-options", response_model=TailoringOptionsBase)
def get_tailoring_options(current_user=Depends(get_current_user)):
    """Get current user's tailoring options"""
    if not current_user.tailoring_options:
        return TailoringOptionsBase()
    return current_user.tailoring_options


@router.put("/me/tailoring-options", response_model=TailoringOptions)
def update_tailoring_options(
    tailoring_options: TailoringOptionsBase,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's tailoring options"""
    db_tailoring_options = (
        db.query(db_models.TailoringOptions)
        .filter(db_models.TailoringOptions.user_id == current_user.id)
        .first()
    )

    if db_tailoring_options:
        db_tailoring_options.ai_model = tailoring_options.ai_model
        db_tailoring_options.resume_template = tailoring_options.resume_template
        db_tailoring_options.last_updated = datetime.now(timezone.utc)
    else:
        db_tailoring_options = db_models.TailoringOptions(
            user_id=current_user.id,
            ai_model=tailoring_options.ai_model,
            resume_template=tailoring_options.resume_template,
        )
        db.add(db_tailoring_options)

    db.commit()
    db.refresh(db_tailoring_options)
    return db_tailoring_options


@router.post("/me/resume/upload", response_model=Resume)
async def upload_resume_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """Upload a resume PDF to update the user's resume content"""
    start_time = datetime.now()
    logger.info(f"Starting resume upload for user {current_user.id}")

    # Check if file is PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    # Read the PDF contents
    pdf_contents = await file.read()

    # Extract text from PDF
    try:
        # Extract raw text from PDF
        resume_content = await extract_text_from_pdf(pdf_contents)

        if not resume_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF",
            )
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}",
        )

    # Save the PDF file
    resume_file_path = None
    try:
        # Convert to base64 for storage
        base64_data = base64.b64encode(pdf_contents).decode("utf-8")
        resume_file_path = save_base64_pdf(base64_data)
    except Exception as e:
        logger.error(f"Error saving PDF file: {e}")
        # Continue even if file save fails - we'll still update the text content

    # Check if user already has a resume
    resume = (
        db.query(db_models.Resume)
        .filter(db_models.Resume.user_id == current_user.id)
        .first()
    )

    if resume:
        # Update existing resume with raw content
        resume.resume_content = resume_content
        resume.resume_file_path = resume_file_path or resume.resume_file_path
        resume.last_updated = datetime.now(timezone.utc)
    else:
        # Create new resume with raw content
        resume = db_models.Resume(
            user_id=current_user.id,
            resume_content=resume_content,
            resume_file_path=resume_file_path,
        )
        db.add(resume)

    db.commit()

    # DUAL STORAGE: Upload original resume to Supabase cloud storage
    if pdf_contents:
        try:
            safe_upload_with_fallback(
                storage_service.upload_original_resume, current_user.id, pdf_contents
            )
        except Exception as e:
            logger.error(f"Cloud storage upload failed during resume upload: {e}")

    # Format the resume content in the background
    background_tasks.add_task(
        process_resume_background,
        current_user.id,
        resume_content,
    )

    end_time = datetime.now()
    logger.info(
        f"Resume upload endpoint completed in {(end_time - start_time).total_seconds()} seconds"
    )

    return resume


@router.get("/me/preferences", response_model=UserPreference)
def get_user_preferences(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's preferences"""
    preferences = (
        db.query(db_models.UserPreferences)
        .filter(db_models.UserPreferences.user_id == current_user.id)
        .first()
    )
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No preferences found for this user.",
        )
    return preferences


@router.post("/me/preferences", response_model=UserPreference)
def add_user_preference(
    preference_data: UserPreferenceCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a new preference to the user's existing preferences"""
    # First, check if the user already has preference data
    preferences = (
        db.query(db_models.UserPreferences)
        .filter(db_models.UserPreferences.user_id == current_user.id)
        .first()
    )

    # Get existing preferences text (if any)
    existing_preferences_text = (
        preferences.preferences_text
        if preferences and preferences.preferences_text
        else "No preferences"
    )

    # Format the preferences using OpenAI
    try:
        formatted_preferences = format_user_preferences(
            existing_preferences=existing_preferences_text,
            new_preference=preference_data.preference,
        )
    except Exception as e:
        logger.error(f"Error formatting preferences with OpenAI: {e}")
        # Fallback to simple concatenation if OpenAI fails
        if existing_preferences_text:
            formatted_preferences = (
                f"{existing_preferences_text}\n{preference_data.preference}"
            )
        else:
            formatted_preferences = preference_data.preference

    if preferences:
        # Update existing preferences with formatted text
        preferences.preferences_text = formatted_preferences
    else:
        # Create new preferences record with formatted text
        preferences = db_models.UserPreferences(
            user_id=current_user.id, preferences_text=formatted_preferences
        )
        db.add(preferences)

    db.commit()
    db.refresh(preferences)
    return preferences
