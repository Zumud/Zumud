"""Anonymous resume tailoring for the landing-page demo (no authentication)."""

import base64
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.core import ai_service
from backend.core.storage_service import safe_upload_with_fallback, storage_service
from backend.models import db_models
from backend.models.db import get_db
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import extract_text_from_pdf
from backend.utils.path_ops import create_new_application_path

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/resume/anonymous/{session_id}")
async def get_anonymous_resume(session_id: str, db: Session = Depends(get_db)):
    """Retrieve an anonymous resume by session ID"""
    session_record = (
        db.query(db_models.AnonymousResumeSession)
        .filter(db_models.AnonymousResumeSession.session_id == session_id)
        .first()
    )

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Check if session is expired
    if datetime.now() > session_record.expires_at:
        db.delete(session_record)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session expired"
        )

    return {
        "session_id": session_record.session_id,
        "pdf_base64": session_record.pdf_base64,
        "company_name": session_record.company_name,
        "generated_at": session_record.generated_at,
        "filename": session_record.filename,
    }


@router.post("/resume/anonymous")
async def generate_anonymous_resume(
    job_description: str = Form(...),
    resume_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Generate a tailored resume without authentication for landing page demo"""
    try:
        # Validate input - must have either text or file
        if not resume_text and not resume_file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either resume_text or resume_file must be provided",
            )

        # If file is provided, extract text from it
        if resume_file:
            if not resume_file.filename.endswith(".pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are supported",
                )

            # Validate file size (5MB limit)
            contents = await resume_file.read()
            if len(contents) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size exceeds 5MB limit",
                )

            try:
                resume_text = await extract_text_from_pdf(contents)
                if not resume_text.strip():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Could not extract text from the PDF",
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error processing PDF: {str(e)}",
                )

        # Generate a session ID for tracking
        session_id = str(uuid.uuid4())

        # Extract company name from job description
        company_name = ai_service.get_company_name(job_description)

        # Create a temporary path for the anonymous user
        timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
        anonymous_username = f"anonymous_{session_id[:8]}"
        save_path = create_new_application_path(
            anonymous_username, company_name, timestamp
        )

        # Default AI model and template; watermark for anonymous users
        tailoring_options = TailoringOptionsBase()
        (
            latex_compiler_response,
            _,
            structured_resume_json,
        ) = await ai_service.generate_structured_latex_resume_async(
            str(save_path),
            resume_text,
            job_description,
            tailoring_options.ai_model,
            tailoring_options.resume_template,
            None,  # No user preferences for anonymous users
            None,  # No user ID for anonymous users
            None,  # No database session for anonymous users
            is_anonymous=True,  # Add watermark for anonymous users
        )

        # Convert PDF to base64 for the frontend
        pdf_base64 = base64.b64encode(latex_compiler_response.content).decode("utf-8")

        structured_resume = json.loads(structured_resume_json)
        name = (
            structured_resume.get("personal_info", {}).get("name", "Resume")
            if structured_resume.get("personal_info", {}).get("name")
            else "Resume"
        )
        filename = f"{name}_{timestamp}_{company_name}.pdf"

        # Store session data in the database with 24-hour expiration
        expires_at = datetime.now() + timedelta(hours=24)
        session_record = db_models.AnonymousResumeSession(
            session_id=session_id,
            pdf_base64=pdf_base64,
            company_name=company_name,
            generated_at=timestamp,
            filename=filename,
            expires_at=expires_at,
        )

        db.add(session_record)
        db.commit()

        # Clean up old expired sessions (best effort)
        try:
            expired_sessions = (
                db.query(db_models.AnonymousResumeSession)
                .filter(db_models.AnonymousResumeSession.expires_at < datetime.now())
                .all()
            )

            for expired_session in expired_sessions:
                db.delete(expired_session)

            if expired_sessions:
                db.commit()
        except Exception as cleanup_error:
            logger.warning(
                f"Warning: Failed to clean up expired sessions: {cleanup_error}"
            )

        # DUAL STORAGE: Upload to Supabase cloud storage
        # This runs after local storage succeeds and doesn't affect the API response
        try:
            safe_upload_with_fallback(
                storage_service.upload_anonymous_resume,
                session_id,
                company_name,
                latex_compiler_response.content,  # PDF content
                filename,
            )
        except Exception as e:
            logger.error(f"Cloud storage upload failed for anonymous resume: {e}")

        return {
            "session_id": session_id,
            "pdf_base64": pdf_base64,
            "company_name": company_name,
            "generated_at": timestamp,
            "filename": filename,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in anonymous resume generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate anonymous resume: {str(e)}",
        )
