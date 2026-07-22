"""Cover-letter generation, downloads, and instruction-based edits."""

import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, PlainTextResponse

from backend.api.applications.common import (
    bill_safely,
    require_resume_content,
    require_resume_record,
    upload_to_cloud,
)
from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.core.storage_service import storage_service
from backend.core.stripe_billing_service import check_payment_method_required
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import PDFGenerator
from backend.utils.path_ops import (
    create_new_application_path,
    create_session_aware_path,
    get_current_application_path,
    get_current_session_info,
    get_or_create_application,
)

router = APIRouter()

logger = logging.getLogger(__name__)


def _read_pdf_if_exists(path: str) -> bytes | None:
    """Best-effort read of a just-generated PDF for the cloud mirror."""
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Could not read generated PDF for cloud upload: {e}")
    return None


@router.get("/cover-letter/plain")
def generate_tailored_plain_coverletter(
    job_description: str = Query(
        ..., description="The job description to tailor the cover letter for"
    ),
    is_new_application: Optional[bool] = Query(
        None,
        description="Whether to create a new job application. If not provided, reuses existing application if available.",
    ),
    current_user=Depends(get_current_user),
) -> str:
    """Generate a tailored plain text cover letter based on job description"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)
    require_resume_content(current_user, before="before generating a cover letter")

    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    cover_letter_text = ai_service.generate_tailored_coverletter_text(
        current_user.resumes.resume_content, job_description, tailoring_options.ai_model
    )

    company_name = ai_service.get_company_name(job_description)
    save_path = get_or_create_application(
        current_user.username, company_name, is_new_application
    )

    # Save the plain text version for future editing
    text_file_path = os.path.join(save_path, "CoverLetter.txt")
    with open(text_file_path, "w") as f:
        f.write(cover_letter_text)

    # Generate PDF
    pdf_generator = PDFGenerator()
    pdf_path = pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )

    pdf_content = _read_pdf_if_exists(pdf_path)

    upload_to_cloud(
        current_user.username,
        "cover letter generation",
        storage_service.upload_cover_letter,
        current_user.id,
        company_name,
        cover_letter_text,  # Text content
        pdf_content,  # PDF content
    )

    bill_safely("coverletter", current_user)

    return cover_letter_text


@router.get("/cover-letter/pdf", response_class=FileResponse)
def download_cover_letter_pdf(current_user=Depends(get_current_user)):
    """Download the generated cover letter as a PDF file"""
    require_resume_record(current_user)

    save_path = get_current_application_path(current_user.username)
    company_name = os.path.basename(save_path).split("_")[-1]
    pdf_file_path = os.path.join(save_path, "CoverLetter.pdf")

    if not os.path.exists(pdf_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter PDF found. Please generate a cover letter first.",
        )

    timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
    return FileResponse(
        path=pdf_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_cover_letter.pdf",
        media_type="application/pdf",
    )


@router.get("/cover-letter/text", response_class=PlainTextResponse)
def get_cover_letter_text_content(current_user=Depends(get_current_user)):
    """Get the raw content of the cover letter text file"""
    require_resume_record(current_user)

    save_path = get_current_application_path(current_user.username)
    text_file_path = os.path.join(save_path, "CoverLetter.txt")

    if not os.path.exists(text_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter text file found. Please generate a cover letter first.",
        )

    with open(text_file_path, "r") as f:
        return f.read()


@router.get("/cover-letter/edit", response_class=FileResponse)
async def edit_cover_letter_with_instructions(
    edit_instruction: str = Query(
        ..., description="Free-form text instructions for editing the cover letter"
    ),
    job_description: str = Query(
        ..., description="The job description to tailor the cover letter for"
    ),
    current_user=Depends(get_current_user),
):
    """Update a cover letter based on free-form text instructions and return the updated PDF"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)

    # Get the current application path to read the existing cover letter
    current_save_path = get_current_application_path(current_user.username)
    cover_letter_file_path = os.path.join(current_save_path, "CoverLetter.pdf")

    require_resume_content(current_user)

    if not os.path.exists(cover_letter_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter found. Please generate a cover letter first.",
        )

    # We need the original cover letter text to edit it
    text_file_path = os.path.join(current_save_path, "CoverLetter.txt")
    if not os.path.exists(text_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter text not found. Please generate a new cover letter.",
        )

    with open(text_file_path, "r") as f:
        cover_letter_text = f.read()

    # Create a new versioned path that preserves the existing session ID
    company_name = os.path.basename(current_save_path).split("_")[-1]
    timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
    session_info = get_current_session_info(current_user.username)

    if session_info:
        existing_session_id, _ = session_info
        new_save_path, _, _ = create_session_aware_path(
            current_user.username,
            company_name,
            session_id=existing_session_id,  # Preserve existing session ID
            timestamp=timestamp,
        )
    else:
        # Fallback: create new application if no session exists
        new_save_path = create_new_application_path(
            current_user.username, company_name, timestamp
        )

    try:
        updated_cover_letter = ai_service.update_cover_letter_with_instructions(
            cover_letter_text,
            current_user.resumes.resume_content,
            job_description,
            edit_instruction,
        )

        # Save the updated cover letter text
        new_text_file_path = os.path.join(new_save_path, "CoverLetter.txt")
        with open(new_text_file_path, "w") as f:
            f.write(updated_cover_letter)

        # Generate a PDF from the updated cover letter
        pdf_generator = PDFGenerator()
        pdf_generator.create_pdf_document(
            updated_cover_letter,
            output_folder=str(new_save_path),
        )
        new_pdf_file_path = os.path.join(new_save_path, "CoverLetter.pdf")

        pdf_content = _read_pdf_if_exists(new_pdf_file_path)

        upload_to_cloud(
            current_user.username,
            "cover letter edit",
            storage_service.upload_cover_letter,
            current_user.id,
            company_name,
            updated_cover_letter,  # Text content
            pdf_content,  # PDF content
        )

        return FileResponse(
            path=new_pdf_file_path,
            filename=f"{current_user.username}_{timestamp}_{company_name}_updated_cover_letter.pdf",
            media_type="application/pdf",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cover letter: {str(e)}",
        )
    finally:
        bill_safely("coverletter_edit", current_user)
