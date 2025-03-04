from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import backend.core.ai_service as ai_service
from backend.models.profile import Profile, Resume
from backend.models.question import Question
from backend.models.tailoring_options import TailoringOptions
from backend.models.templates import (
    john_doe_preferences,
    john_doe_resume,
)
from backend.utils.file_ops import PDFGenerator, save_pdf
from backend.utils.path_ops import create_new_application_path, get_current_application_path
from backend.models.db import get_db
from backend.models.db_models import User

func_router = APIRouter(tags=["functions"])

@func_router.post("/determine_eligibility")
def determine_eligibility(job_description: str, profile: Profile = Profile(resume=Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions(), db: Session = Depends(get_db)):
    """
    Gets profile and job description and determines eligibility for applying to the job
    """
    # Fetch legal authorization from database
    user = db.query(User).filter(User.username == profile.username).first()
    if not user or not user.legal_authorization:
        return {
            "eligibility": False,
            "reason": "Legal authorization information not found for user"
        }
    
    legal_auth = user.legal_authorization
    eligibility, reason = ai_service.consider_eligibility(job_description, legal_auth, tailoring_options.ai_model)
    return {
        "eligibility": eligibility,
        "reason": reason
    }

@func_router.post("/determine_suitability")
def determine_suitability(job_description: str, profile: Profile = Profile(resume=Resume(john_doe_resume), preferences=john_doe_preferences), tailoring_options: TailoringOptions = TailoringOptions()):
    """
    Gets profile and job description and determines suitability for applying to the job 
    """
    suitability, reason = ai_service.consider_suitability(job_description, profile.preferences, tailoring_options.ai_model)
    return {
        "suitability": suitability,
        "reason": reason
    }

@func_router.post("/generate-tailored-plain-resume")
def generate_tailored_plain_resume(job_description: str, profile: Profile = Profile(resume=Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a string
    """
    return ai_service.create_tailored_plain_resume(profile.resume.text, job_description, tailoring_options.ai_model, tailoring_options.resume_template)

@func_router.post("/generate-tailored-plain-coverletter")
def generate_tailored_plain_coverletter(job_description: str, profile: Profile = Profile(Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()) -> str:  # We should not pass tailoring options everytime, should be a config for each user. It could be kept with a session for example.
    """
    Gets resume and job description in plain text and returns customized cover letter as a string
    """
    cover_letter_text = ai_service.create_tailored_plain_coverletter(profile.resume.text, job_description, tailoring_options.ai_model)
    
    # Generate the PDF - use existing application path if available
    save_path = get_current_application_path()
    
    pdf_generator = PDFGenerator()
    output_path = pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )
    return cover_letter_text + f"\n\nCover letter saved at: {output_path}"

@func_router.post("/generate-latex-resume-save")
def generate_tailored_latex_resume_save(job_description: str, profile: Profile = Profile(Resume(john_doe_resume)), tailoring_options: TailoringOptions = TailoringOptions()):
    """
    Gets resume and job description in plain text and saves tailored resume
    """
    # Extract company name from job description
    company_name = ai_service.get_company_name(job_description)
    
    # Always create a new application folder for a new resume
    save_path = create_new_application_path(company_name)
    tailored_plain_resume = generate_tailored_plain_resume(job_description, profile, tailoring_options)
    
    latex_compiler_response, latex_code = ai_service.covert_plain_resume_to_latex(
        str(save_path),
        tailored_plain_resume,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )
    username = profile.username
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, username)
    
    return {
        "success": f"Generated resume saved at here: {pdf_file_path}",
        "pdf_file_path": pdf_file_path,
        "latex_code": latex_code
    }

@func_router.post("/answer-application-questions")
def answer_application_questions(
    job_description: str,
    question: Question,
    profile: Profile = Profile(Resume(john_doe_resume)),
    tailoring_options: TailoringOptions = TailoringOptions()
) -> str:
    """
    Gets resume, job description, and questions in the job applicaton and answer to them based on resume and job description.
    """
    # Use existing application path if available
    save_path = get_current_application_path()
    return ai_service.generate_answer_questions(
        profile.resume.text,
        job_description,
        question.description,
        str(save_path),
        tailoring_options.ai_model
    )
