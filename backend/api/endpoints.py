from fastapi import APIRouter, Depends, HTTPException, status

import backend.core.ai_service as ai_service
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import PDFGenerator, save_pdf
from backend.utils.path_ops import create_new_application_path, get_current_application_path
from backend.api.auth import get_current_user

func_router = APIRouter(tags=["functions"])

@func_router.post("/determine_eligibility")
def determine_eligibility(job_description: str, current_user = Depends(get_current_user)):
    """
    Gets profile and job description and determines eligibility for applying to the job
    """
    # Fetch legal authorization from database
    if not current_user.legal_authorization:
        return {
            "eligibility": False,
            "reason": "Legal authorization information not found for user"
        }
    
    legal_auth = current_user.legal_authorization
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    eligibility, reason = ai_service.consider_eligibility(job_description, legal_auth, tailoring_options.ai_model)
    return {
        "eligibility": eligibility,
        "reason": reason
    }

@func_router.post("/determine_suitability")
def determine_suitability(job_description: str, current_user = Depends(get_current_user)):
    """
    Gets profile and job description and determines suitability for applying to the job 
    """
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    suitability, reason = ai_service.consider_suitability(job_description, tailoring_options.ai_model)
    return {"suitability": suitability, "reason": reason}

@func_router.post("/generate-tailored-plain-resume")
def generate_tailored_plain_resume(job_description: str, current_user = Depends(get_current_user)) -> str:
    """
    Gets resume and job description in plain text and returns tailored resume as a string
    """
    if not current_user.resumes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a resume")
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.create_tailored_plain_resume(current_user.resumes.resume_content, job_description, tailoring_options.ai_model, tailoring_options.resume_template)

@func_router.post("/generate-tailored-plain-coverletter")
def generate_tailored_plain_coverletter(job_description: str, current_user = Depends(get_current_user)) -> str:
    """
    Gets resume and job description in plain text and returns customized cover letter as a string
    """
    if not current_user.resumes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a resume")
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    cover_letter_text = ai_service.create_tailored_plain_coverletter(current_user.resumes.resume_content, job_description, tailoring_options.ai_model)
    
    # Generate the PDF - use existing application path if available
    save_path = get_current_application_path()
    
    pdf_generator = PDFGenerator()
    output_path = pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )
    return cover_letter_text + f"\n\nCover letter saved at: {output_path}"

@func_router.post("/generate-latex-resume-save")
def generate_tailored_latex_resume_save(job_description: str, current_user = Depends(get_current_user)):
    """
    Gets resume and job description in plain text and saves tailored resume
    """
    if not current_user.resumes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a resume")
    
    # Extract company name from job description
    company_name = ai_service.get_company_name(job_description)
    
    # Always create a new application folder for a new resume
    save_path = create_new_application_path(company_name)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    tailored_plain_resume = generate_tailored_plain_resume(job_description, current_user)
    
    latex_compiler_response, latex_code = ai_service.covert_plain_resume_to_latex(
        str(save_path),
        tailored_plain_resume,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)
    
    return {
        "success": f"Generated resume saved at here: {pdf_file_path}",
        "pdf_file_path": pdf_file_path,
        "latex_code": latex_code
    }

@func_router.post("/answer-application-questions")
def answer_application_questions(job_description: str, question: str, current_user = Depends(get_current_user)) -> str:
    """
    Gets resume, job description, and questions in the job application and answers them based on resume and job description.
    """
    if not current_user.resumes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a resume")
    
    # Use existing application path if available
    save_path = get_current_application_path()
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.generate_answer_questions(current_user.resumes.resume_content, job_description, question, str(save_path), tailoring_options.ai_model)
