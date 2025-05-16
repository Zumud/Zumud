from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Body
from datetime import datetime
from fastapi.responses import FileResponse, PlainTextResponse
import uuid
import os
import json

from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.models.tailoring_options import TailoringOptionsBase
from backend.utils.file_ops import PDFGenerator, save_pdf, extract_text_from_pdf
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
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details before generating a tailored resume."
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
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details before generating a cover letter."
        )
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    cover_letter_text = ai_service.generate_tailored_coverletter_text(
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model
    )
    
    save_path = get_current_application_path(current_user.username)
    pdf_generator = PDFGenerator()
    pdf_generator.create_pdf_document(
        cover_letter_text,
        output_folder=str(save_path),
    )
    return cover_letter_text

@router.get("/cover-letter/pdf", response_class=FileResponse)
def download_cover_letter_pdf(
    current_user = Depends(get_current_user)
):
    """Download the generated cover letter as a PDF file"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    # Get the current application path for this user
    save_path = get_current_application_path(current_user.username)
    
    # Generate company name for the filename
    company_name = os.path.basename(save_path).split('_')[-1]
    
    # Check if the PDF file exists
    pdf_file_path = os.path.join(save_path, "CoverLetter.pdf")
    
    if not os.path.exists(pdf_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter PDF found. Please generate a cover letter first."
        )
    
    # Return the PDF file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return FileResponse(
        path=pdf_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_cover_letter.pdf",
        media_type="application/pdf"
    )

@router.get("/resume/pdf", response_class=FileResponse)
def generate_and_save_pdf_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user)
):
    """Generate a tailored resume and return it as a PDF file"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details before generating a PDF."
        )
    
    company_name = ai_service.get_company_name(job_description)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = create_new_application_path(current_user.username, company_name, timestamp)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    latex_compiler_response, _, structured_resume_json = ai_service.generate_structured_latex_resume(
        str(save_path),
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template
    )
    
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)
    
    # Store the structured resume JSON for later use in the session or a temporary file
    # This would be better implemented with a proper session or database storage
    json_file_path = os.path.join(save_path, "resume.json")
    with open(json_file_path, 'w') as f:
        f.write(structured_resume_json)
    
    # Return the PDF file directly
    return FileResponse(
        path=pdf_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_tailored_resume.pdf",
        media_type="application/pdf",
        # Note: We cannot include custom headers with FileResponse easily
        # A better approach would be to create a custom endpoint to retrieve the JSON separately
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

@router.get("/resume/tex/content", response_class=PlainTextResponse)
def get_resume_tex_content(
    current_user = Depends(get_current_user)
):
    """Get the raw content of the .tex file for integration with services like Overleaf"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    # Get the current application path for this user
    save_path = get_current_application_path(current_user.username)
    
    # Check if the tex file exists
    tex_file_path = os.path.join(save_path, "resume.tex")
    
    if not os.path.exists(tex_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No .tex file found. Please generate a resume first."
        )
    
    # Read the content of the file
    with open(tex_file_path, 'r') as f:
        tex_content = f.read()
    
    # Return the raw content
    return tex_content

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
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details before generating answers."
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
    
    # Read the uploaded PDF and extract text
    contents = await file.read()
    resume_text = await extract_text_from_pdf(contents)
    
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

@router.get("/resume/edit", response_class=FileResponse)
async def edit_resume_with_instructions(
    edit_instruction: str = Query(..., description="Free-form text instructions for editing the resume"),
    current_user = Depends(get_current_user)
):
    """Update a resume JSON based on free-form text instructions and return the updated PDF"""
    # Get the current application path to read the existing JSON
    current_save_path = get_current_application_path(current_user.username)
    
    # Check if the JSON file exists
    json_file_path = os.path.join(current_save_path, "resume.json")
    
    if not os.path.exists(json_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume JSON found. Please generate a resume first."
        )
    
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        last_resume_json = f.read()
    
    # Create a new path for the updated resume with a timestamp
    company_name = os.path.basename(current_save_path).split('_')[-1]
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_save_path = create_new_application_path(current_user.username, company_name, timestamp)
    
    # Get user's tailoring options
    # tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    try:
        # Process the edit and generate PDF using the new service function
        latex_compiler_response, updated_resume_json = ai_service.edit_resume_and_generate_pdf(
            str(new_save_path),
            last_resume_json,
            edit_instruction,
            # Use GPT-4.1 Nano which is sufficient for resume edits   
            # tailoring_options.ai_model,
            # tailoring_options.resume_template
        )
        
        # Save the updated JSON to the new path
        new_json_file_path = os.path.join(new_save_path, "resume.json")
        with open(new_json_file_path, 'w') as f:
            f.write(updated_resume_json)
        
        # Save the PDF
        pdf_file_path = save_pdf(str(new_save_path), latex_compiler_response.content, current_user.username)
        
        # Return the PDF file
        return FileResponse(
            path=pdf_file_path,
            filename=f"{current_user.username}_{timestamp}_{company_name}_updated_resume.pdf",
            media_type="application/pdf"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/resume/json")
def get_latest_resume_json(
    current_user = Depends(get_current_user)
):
    """Get the latest generated resume JSON"""
    
    # Get the current application path for this user
    save_path = get_current_application_path(current_user.username)
    
    # Check if the JSON file exists
    json_file_path = os.path.join(save_path, "resume.json")
    
    if not os.path.exists(json_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume JSON found. Please generate a resume first."
        )
    
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        resume_json = f.read()
    
    # Return the JSON
    return {"resume_json": resume_json} 