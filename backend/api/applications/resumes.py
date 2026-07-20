"""Tailored-resume generation, downloads, and instruction-based edits."""

import json
import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from backend.api.applications.common import (
    bill_safely,
    get_preferences_text,
    require_resume_content,
    require_resume_record,
    upload_to_cloud,
)
from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.core.storage_service import storage_service
from backend.core.stripe_billing_service import check_payment_method_required
from backend.models.ai_models import AIModel
from backend.models.db import get_db
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import save_pdf
from backend.utils.path_ops import (
    create_new_application_path,
    create_session_aware_path,
    get_current_application_path,
    get_current_session_info,
    get_or_create_application,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/resume/pdf", response_class=FileResponse)
async def generate_and_save_pdf_resume(
    job_description: str = Query(
        ..., description="The job description to tailor the resume for"
    ),
    is_new_application: Optional[bool] = Query(
        None,
        description="Whether to create a new job application. If not provided, creates a new application by default.",
    ),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a tailored resume and return it as a PDF file"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)
    require_resume_content(current_user, before="before generating a PDF")

    user_preferences = get_preferences_text(db, current_user.id)

    company_name = ai_service.get_company_name(job_description)
    save_path = get_or_create_application(
        current_user.username, company_name, is_new_application
    )
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()

    (
        latex_compiler_response,
        tex_content,
        structured_resume_json,
    ) = await ai_service.generate_structured_latex_resume_async(
        str(save_path),
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template,
        user_preferences,
        current_user.id,
        db,
        is_anonymous=False,  # Authenticated users get no watermark
    )

    # Save files locally
    pdf_file_path = save_pdf(
        str(save_path), latex_compiler_response.content, current_user.username
    )

    # Store the structured resume JSON so the edit endpoint can pick it up later
    json_file_path = os.path.join(save_path, "resume.json")
    with open(json_file_path, "w") as f:
        f.write(structured_resume_json)

    upload_to_cloud(
        current_user.username,
        "resume generation",
        storage_service.upload_tailored_resume,
        current_user.id,
        company_name,
        latex_compiler_response.content,  # PDF content
        tex_content,  # TEX content
        structured_resume_json,  # JSON content
    )

    structured_resume = json.loads(structured_resume_json)
    name = (
        structured_resume.get("personal_info", {}).get("name", "")
        if structured_resume.get("personal_info", {}).get("name")
        else ""
    )
    timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")

    bill_safely("resume", current_user)

    return FileResponse(
        path=pdf_file_path,
        filename=f"{name}_{timestamp}_{company_name}.pdf",
        media_type="application/pdf",
    )


@router.get("/resume/tex", response_class=FileResponse)
def get_resume_tex_file(current_user=Depends(get_current_user)):
    """Get the .tex file of a tailored resume based on job description"""
    require_resume_record(current_user)

    save_path = get_current_application_path(current_user.username)
    company_name = os.path.basename(save_path).split("_")[-1]
    tex_file_path = os.path.join(save_path, "resume.tex")

    if not os.path.exists(tex_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No .tex file found. Please generate a resume first.",
        )

    timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
    return FileResponse(
        path=tex_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_resume.tex",
        media_type="application/x-tex",
    )


@router.get("/resume/tex/content", response_class=PlainTextResponse)
def get_resume_tex_content(current_user=Depends(get_current_user)):
    """Get the raw content of the .tex file for integration with services like Overleaf"""
    require_resume_record(current_user)

    save_path = get_current_application_path(current_user.username)
    tex_file_path = os.path.join(save_path, "resume.tex")

    if not os.path.exists(tex_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No .tex file found. Please generate a resume first.",
        )

    with open(tex_file_path, "r") as f:
        return f.read()


@router.get("/resume/json")
def get_latest_resume_json(current_user=Depends(get_current_user)):
    """Get the latest generated resume JSON"""
    save_path = get_current_application_path(current_user.username)
    json_file_path = os.path.join(save_path, "resume.json")

    if not os.path.exists(json_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume JSON found. Please generate a resume first.",
        )

    with open(json_file_path, "r") as f:
        resume_json = f.read()

    return {"resume_json": resume_json}


@router.get("/resume/edit", response_class=FileResponse)
async def edit_resume_with_instructions(
    edit_instruction: str = Query(
        ..., description="Free-form text instructions for editing the resume"
    ),
    job_description: str = Query(
        ..., description="The job description to tailor the resume for"
    ),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a resume JSON based on free-form text instructions and return the updated PDF"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)
    require_resume_content(current_user)

    # Get the current application path to read the existing JSON
    current_save_path = get_current_application_path(current_user.username)
    json_file_path = os.path.join(current_save_path, "resume.json")

    if not os.path.exists(json_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume JSON found. Please generate a resume first.",
        )

    with open(json_file_path, "r") as f:
        last_resume_json = f.read()

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

    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()

    try:
        latex_compiler_response, updated_resume_json, tex_content = (
            ai_service.update_resume_with_instructions(
                last_resume_json,
                job_description,
                edit_instruction,
                str(new_save_path),
                AIModel.gpt_4_1_nano,
                tailoring_options.resume_template,  # Use user's template preference
                current_user.id,
                db,
            )
        )

        # Save the updated JSON, TEX, and PDF to the new path
        with open(os.path.join(new_save_path, "resume.json"), "w") as f:
            f.write(updated_resume_json)
        with open(
            os.path.join(new_save_path, "resume.tex"), "w", encoding="utf-8"
        ) as f:
            f.write(tex_content)
        pdf_file_path = save_pdf(
            str(new_save_path), latex_compiler_response.content, current_user.username
        )

        upload_to_cloud(
            current_user.username,
            "resume edit",
            storage_service.upload_tailored_resume,
            current_user.id,
            company_name,
            latex_compiler_response.content,  # PDF content
            tex_content,  # TEX content
            updated_resume_json,  # Updated JSON content
        )

        return FileResponse(
            path=pdf_file_path,
            filename=f"{current_user.username}_{timestamp}_{company_name}_updated_resume.pdf",
            media_type="application/pdf",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        bill_safely("resume_edit", current_user)
