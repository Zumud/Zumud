from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from datetime import datetime
from fastapi.responses import FileResponse
import io
import PyPDF2
import uuid
import os

from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import PDFGenerator, save_pdf
from backend.utils.path_ops import create_new_application_path, get_current_application_path

router = APIRouter(prefix="/applications", tags=["applications"])

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
    
    save_path = get_current_application_path(current_user.username)
    pdf_generator = PDFGenerator()
    output_path = pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )
    return cover_letter_text + f"\n\nCover letter saved at: {output_path}"

@router.get("/resume/pdf", response_class=FileResponse)
def generate_and_save_pdf_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user)
):
    """Generate a tailored resume and return it as a PDF file"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    company_name = ai_service.get_company_name(job_description)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = create_new_application_path(current_user.username, company_name, timestamp)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    latex_compiler_response, _ = ai_service.generate_structured_latex_resume(
        str(save_path),
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )
    
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)
    
    # Return the PDF file directly
    return FileResponse(
        path=pdf_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_tailored_resume.pdf",
        media_type="application/pdf"
    )

@router.get("/resume/tex", response_class=FileResponse)
def get_resume_tex_file(
    current_user = Depends(get_current_user)
):
    """Get the .tex file of a tailored resume based on job description"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    # Get the current application path for this user
    save_path = get_current_application_path(current_user.username)
    
    # Generate company name for the filename
    company_name = os.path.basename(save_path).split('_')[-1]
    
    # Check if the tex file exists
    tex_file_path = os.path.join(save_path, "resume.tex")
    
    if not os.path.exists(tex_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No .tex file found. Please generate a resume first."
        )
    
    # Return the .tex file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return FileResponse(
        path=tex_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_resume.tex",
        media_type="application/x-tex"
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
    
    save_path = get_current_application_path(current_user.username)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.generate_answer_questions(
        current_user.resumes.resume_content,
        job_description,
        question,
        str(save_path),
        tailoring_options.ai_model
    ) 

@router.post("/resume/improve")
async def improve_resume_pdf(
    file: UploadFile = File(...)
):
    """Improve an uploaded resume PDF and return a professional version"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Read the uploaded PDF
    contents = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
    
    # Extract text from all pages
    resume_text = ""
    for page in pdf_reader.pages:
        resume_text += page.extract_text()
    
    if not resume_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the PDF"
        )
    
    # Generate a random username for anonymous users
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    anonymous_username = f"anonymous_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # Create a save path
    save_path = create_new_application_path(anonymous_username, "improved_resume")

    tailoring_options = TailoringOptionsBase()
    
    # Generate improved resume using AI with default options
    latex_compiler_response, _ = ai_service.generate_structured_latex_resume(
        str(save_path),
        resume_text,
        "There is no specific job description for general improvement",  # No specific job description for general improvement
        tailoring_options.ai_model,  # Default AI model
        tailoring_options.resume_template  # Default template
    )
    
    # Save the improved PDF
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, anonymous_username)
    
    return FileResponse(
        path=pdf_file_path,
        filename=f"{timestamp}_improved_resume.pdf",
        media_type="application/pdf"
    ) 