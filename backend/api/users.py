import base64
import logging
from datetime import datetime, timezone

import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from pydantic import BaseModel, EmailStr, SecretStr
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.api.auth import get_current_user
from backend.config.envs import SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL
from backend.core import template_service
from backend.core.storage_service import safe_upload_with_fallback, storage_service
from backend.models import db_models
from backend.models.ai_rule_models import (
    UserAIRule,
    UserAIRuleCreate,
    UserAIRuleUpdate,
)
from backend.models.db import SessionLocal, get_db
from backend.models.resume_models import Resume, ResumeBase
from backend.models.template_models import TemplateSelection, TemplateSummary
from backend.models.user_models import User
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


class IdentifierCheckRequest(BaseModel):
    identifier: str


class UsernameSignInRequest(BaseModel):
    username: str
    password: SecretStr


def _email_auth_methods(email: str, db: Session):
    return db.execute(
        text(
            """
            SELECT
              EXISTS (
                SELECT 1 FROM auth.users WHERE lower(email) = :email
              ) AS does_exist,
              EXISTS (SELECT 1 FROM auth.users
                      WHERE lower(email) = :email
                        AND encrypted_password IS NOT NULL
                        AND encrypted_password <> '') AS has_password,
              EXISTS (SELECT 1 FROM auth.identities i
                      JOIN auth.users u ON u.id = i.user_id
                      WHERE lower(u.email) = :email
                        AND i.provider = 'google') AS has_google
            """
        ),
        {"email": email},
    ).first()


def _username_auth_record(username: str, db: Session):
    return (
        db.execute(
            text(
                """
            SELECT
              au.email AS email,
              (au.encrypted_password IS NOT NULL
               AND au.encrypted_password <> '') AS has_password,
              EXISTS (
                SELECT 1
                FROM auth.identities i
                WHERE i.user_id = au.id AND i.provider = 'google'
              ) AS has_google
            FROM public.users pu
            JOIN auth.users au
              ON au.id = pu.supabase_uid
              OR (
                pu.supabase_uid IS NULL
                AND pu.email IS NOT NULL
                AND lower(au.email) = lower(pu.email)
              )
            WHERE lower(pu.username) = :username
            LIMIT 1
            """
            ),
            {"username": username},
        )
        .mappings()
        .first()
    )


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
        row = _email_auth_methods(email, db)
    except Exception as e:
        # Fail safe: never block the UI if the auth-schema read fails.
        logger.error(f"check-email lookup failed: {e}")
        return {"exists": False, "has_password": False, "has_google": False}

    return {
        "exists": bool(row[0]),
        "has_password": bool(row[1]),
        "has_google": bool(row[2]),
    }


@router.post("/check-identifier")
def check_identifier(payload: IdentifierCheckRequest, db: Session = Depends(get_db)):
    """Report sign-in methods for either an email address or username."""
    identifier = payload.identifier.strip().lower()
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Enter an email address or username.",
        )

    try:
        if "@" in identifier:
            row = _email_auth_methods(identifier, db)
            return {
                "identifier_type": "email",
                "exists": bool(row[0]),
                "has_password": bool(row[1]),
                "has_google": bool(row[2]),
            }

        record = _username_auth_record(identifier, db)
        return {
            "identifier_type": "username",
            "exists": record is not None,
            "has_password": bool(record and record["has_password"]),
            "has_google": bool(record and record["has_google"]),
        }
    except Exception as e:
        logger.error("check-identifier lookup failed: %s", e)
        if "@" in identifier:
            # Preserve the existing email-first fail-safe: Supabase will still
            # validate the address if the user continues to account creation.
            return {
                "identifier_type": "email",
                "exists": False,
                "has_password": False,
                "has_google": False,
            }
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sign-in is temporarily unavailable. Please try again.",
        ) from e


@router.post("/sign-in/username")
async def sign_in_with_username(
    payload: UsernameSignInRequest,
    api_response: Response,
    db: Session = Depends(get_db),
):
    """Exchange a username and password for a Supabase Auth session."""
    username = payload.username.strip().lower()
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password.",
        )

    try:
        record = _username_auth_record(username, db)
    except Exception as e:
        logger.error("Username sign-in lookup failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sign-in is temporarily unavailable. Please try again.",
        ) from e

    if not record or not record["email"] or not record["has_password"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password.",
        )

    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        logger.error("Username sign-in requires Supabase URL and publishable key")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sign-in is temporarily unavailable. Please try again.",
        )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            auth_response = await client.post(
                f"{SUPABASE_URL.rstrip('/')}/auth/v1/token",
                params={"grant_type": "password"},
                headers={"apikey": SUPABASE_PUBLISHABLE_KEY},
                json={
                    "email": record["email"],
                    "password": payload.password.get_secret_value(),
                },
            )
    except httpx.RequestError as e:
        logger.error("Supabase username sign-in request failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Sign-in is temporarily unavailable. Please try again.",
        ) from e

    if auth_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many sign-in attempts. Please try again later.",
        )
    if (
        auth_response.status_code
        in {
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        }
        or auth_response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        logger.error(
            "Supabase username sign-in failed with status %s",
            auth_response.status_code,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Sign-in is temporarily unavailable. Please try again.",
        )
    if auth_response.is_error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password.",
        )

    try:
        session = auth_response.json()
        access_token = session["access_token"]
        refresh_token = session["refresh_token"]
        if not isinstance(access_token, str) or not access_token:
            raise ValueError("Missing access token")
        if not isinstance(refresh_token, str) or not refresh_token:
            raise ValueError("Missing refresh token")
    except (KeyError, TypeError, ValueError) as e:
        logger.error("Supabase username sign-in returned an invalid session")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Sign-in is temporarily unavailable. Please try again.",
        ) from e

    api_response.headers["Cache-Control"] = "no-store"
    api_response.headers["Pragma"] = "no-cache"
    return {"access_token": access_token, "refresh_token": refresh_token}


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


def _get_current_user_ai_rule(
    rule_id: int, user_id: int, db: Session
) -> db_models.UserAIRule:
    rule = (
        db.query(db_models.UserAIRule)
        .filter(
            db_models.UserAIRule.id == rule_id,
            db_models.UserAIRule.user_id == user_id,
        )
        .first()
    )
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI rule not found.",
        )
    return rule


@router.get("/me/ai-rules", response_model=list[UserAIRule])
def list_user_ai_rules(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """List the authenticated user's AI rules."""
    return (
        db.query(db_models.UserAIRule)
        .filter(db_models.UserAIRule.user_id == current_user.id)
        .order_by(
            db_models.UserAIRule.updated_at.desc(),
            db_models.UserAIRule.id.asc(),
        )
        .all()
    )


@router.post(
    "/me/ai-rules",
    response_model=UserAIRule,
    status_code=status.HTTP_201_CREATED,
)
def create_user_ai_rule(
    rule_data: UserAIRuleCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create an AI rule for the authenticated user."""
    rule = db_models.UserAIRule(
        user_id=current_user.id,
        title=rule_data.title,
        instruction=rule_data.instruction,
        is_enabled=True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/me/ai-rules/{rule_id}", response_model=UserAIRule)
def update_user_ai_rule(
    rule_id: int,
    rule_data: UserAIRuleUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an AI rule owned by the authenticated user."""
    update_data = rule_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one field to update.",
        )

    rule = _get_current_user_ai_rule(rule_id, current_user.id, db)
    for field, value in update_data.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/me/ai-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_ai_rule(
    rule_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an AI rule owned by the authenticated user."""
    rule = _get_current_user_ai_rule(rule_id, current_user.id, db)
    db.delete(rule)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me/templates", response_model=list[TemplateSummary])
def list_templates(
    current_user=Depends(get_current_user), db: Session = Depends(get_db)
):
    """The templates the user can choose between, and which one is in use."""
    return template_service.available_templates(current_user.id, db)


@router.put("/me/templates/selected", response_model=list[TemplateSummary])
def select_template(
    selection: TemplateSelection,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Choose the template this user's resumes render with."""
    try:
        template_service.select_template(selection.slug, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return template_service.available_templates(current_user.id, db)


@router.post(
    "/me/templates",
    response_model=list[TemplateSummary],
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_template(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str | None = Form(None),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Accept a .tex file and start turning it into a template.

    Accepted rather than created: converting takes a model several attempts and a
    real compile each time, far longer than a request should be held open. The
    returned gallery carries the new template as pending, and the client follows it
    from there.
    """
    # Capped rather than unbounded, and one byte past the limit so the guard can
    # tell "at the limit" from "over it".
    raw = await file.read(template_service.MAX_UPLOAD_BYTES + 1)

    try:
        template = template_service.accept_upload(
            file.filename or "", raw, name, current_user.id, db
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    background_tasks.add_task(template_service.convert_upload, template.id)
    return template_service.available_templates(current_user.id, db)


@router.delete("/me/templates/{slug}", response_model=list[TemplateSummary])
def delete_template(
    slug: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete one of the user's own templates."""
    try:
        template_service.delete_template(slug, current_user.id, db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return template_service.available_templates(current_user.id, db)
