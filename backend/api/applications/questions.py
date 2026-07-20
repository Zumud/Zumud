"""Application-question answering and instruction-based answer edits."""

import logging
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.applications.common import (
    bill_safely,
    require_resume_content,
    upload_to_cloud,
)
from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.core.storage_service import storage_service
from backend.core.stripe_billing_service import check_payment_method_required
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.path_ops import (
    extract_company_from_local_path,
    get_current_application_path,
    get_or_create_application,
)

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/questions/answer")
def answer_application_questions(
    job_description: str = Query(..., description="The job description to analyze"),
    question: str = Query(..., description="The question to answer"),
    is_new_application: Optional[bool] = Query(
        None,
        description="Whether to create a new job application. If not provided, reuses existing application if available.",
    ),
    current_user=Depends(get_current_user),
) -> str:
    """Generate answers for job application questions based on resume and job description"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)
    require_resume_content(current_user, before="before generating answers")

    # Get or create application path for this user
    company_name = ai_service.get_company_name(job_description)
    save_path = get_or_create_application(
        current_user.username, company_name, is_new_application
    )
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()

    # The AI service saves the Q&A file into the application folder itself
    answer = ai_service.generate_answer_questions(
        current_user.resumes.resume_content,
        job_description,
        question,
        str(save_path),
        tailoring_options.ai_model,
    )

    upload_to_cloud(
        current_user.username,
        "question-answer",
        storage_service.upload_question_answer,
        current_user.id,
        company_name,
        question,
        answer,
        False,  # is_updated = False for new answers
    )

    bill_safely("qa", current_user)

    return answer


@router.get("/questions/answer/edit")
def edit_answer_with_instructions(
    edit_instruction: str = Query(
        ..., description="Instructions for editing the answer"
    ),
    original_answer: str = Query(..., description="The original answer to edit"),
    job_description: str = Query(..., description="The job description context"),
    question: str = Query(..., description="The question being answered"),
    current_user=Depends(get_current_user),
) -> str:
    """Edit an existing answer based on user instructions"""
    # Check if payment method is required before generation
    check_payment_method_required(email=current_user.email, name=current_user.username)
    require_resume_content(current_user, before="before editing answers")

    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()

    try:
        updated_answer = ai_service.update_answer_with_instructions(
            original_answer,
            question,
            job_description,
            current_user.resumes.resume_content,
            edit_instruction,
            tailoring_options.ai_model,
        )

        # Save the Q&A pair in the application folder
        save_path = get_current_application_path(current_user.username)
        qa_file_path = os.path.join(
            save_path, f"question_updated_{datetime.now().strftime('%m%d_%H%M%S')}.txt"
        )
        with open(qa_file_path, "w") as f:
            f.write(
                f"Question: {question}\n\nOriginal Answer: {original_answer}\n\nEdit Instructions: {edit_instruction}\n\nUpdated Answer: {updated_answer}"
            )

        company_name = extract_company_from_local_path(save_path) or "unknown_company"
        upload_to_cloud(
            current_user.username,
            "question-answer edit",
            storage_service.upload_question_answer,
            current_user.id,
            company_name,
            question,
            updated_answer,
            True,  # is_updated = True for edited answers
        )

        return updated_answer

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        bill_safely("qa_edit", current_user)
