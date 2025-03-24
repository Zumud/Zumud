from fastapi import APIRouter, Depends, HTTPException, status, Query

import backend.core.ai_service as ai_service
from backend.models.tailoring_options import TailoringOptionsBase
from backend.models.application_responses import EligibilityResponse, SuitabilityResponse, ApplicationResponse
from backend.utils.file_ops import PDFGenerator, save_pdf
from backend.utils.path_ops import create_new_application_path, get_current_application_path
from backend.api.auth import get_current_user

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/analyze/eligibility", response_model=EligibilityResponse)
def determine_eligibility(
    job_description: str = Query(..., description="The job description to analyze"),
    current_user = Depends(get_current_user)
):
    """Analyze job eligibility based on user profile and job description"""
    if not current_user.legal_authorization:
        return EligibilityResponse(
            eligibility=False,
            reason="Legal authorization information not found for user"
        )
    
    legal_auth = current_user.legal_authorization
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    eligibility, reason = ai_service.consider_eligibility(job_description, legal_auth, tailoring_options.ai_model)
    return EligibilityResponse(eligibility=eligibility, reason=reason)

@router.get("/analyze/suitability", response_model=SuitabilityResponse)
def determine_suitability(
    job_description: str = Query(..., description="The job description to analyze"),
    current_user = Depends(get_current_user)
):
    """Analyze job suitability based on user profile and job description"""
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    suitability, reason = ai_service.consider_suitability(job_description, tailoring_options.ai_model)
    return SuitabilityResponse(suitability=suitability, reason=reason)

@router.get("/resume/plain")
def generate_tailored_plain_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user)
) -> str:
    """Generate a tailored plain text resume based on job description"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.generate_tailored_resume_text(
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )

@router.get("/cover-letter/plain")
def generate_tailored_plain_coverletter(
    job_description: str = Query(..., description="The job description to tailor the cover letter for"),
    current_user = Depends(get_current_user)
) -> str:
    """Generate a tailored plain text cover letter based on job description"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    cover_letter_text = ai_service.generate_tailored_coverletter_text(
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model
    )
    
    save_path = get_current_application_path()
    pdf_generator = PDFGenerator()
    output_path = pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )
    return cover_letter_text + f"\n\nCover letter saved at: {output_path}"

@router.get("/resume/pdf", response_model=ApplicationResponse)
def generate_and_save_pdf_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user)
):
    """Generate a tailored resume and save it as a PDF file"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    company_name = ai_service.get_company_name(job_description)
    save_path = create_new_application_path(company_name)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    latex_compiler_response, latex_code = ai_service.covert_plain_resume_to_latex(
        str(save_path),
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )
    
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)
    
    return ApplicationResponse(
        success=f"Generated resume saved at: {pdf_file_path}",
        pdf_file_path=pdf_file_path,
        latex_code=latex_code
    )

@router.get("/questions/answer")
def answer_application_questions(
    job_description: str = Query(..., description="The job description to analyze"),
    question: str = Query(..., description="The question to answer"),
    current_user = Depends(get_current_user)
) -> str:
    """Generate answers for job application questions based on resume and job description"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    save_path = get_current_application_path()
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.generate_answer_questions(
        current_user.resumes.resume_content,
        job_description,
        question,
        str(save_path),
        tailoring_options.ai_model
    ) 