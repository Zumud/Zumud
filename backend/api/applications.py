from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from datetime import datetime
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session
import uuid
import os
import json

from backend.api.auth import get_current_user
from backend.core import ai_service
from backend.models.ai_models import AIModel
from backend.models.tailoring_options import TailoringOptionsBase
from backend.models.user_models import UserTemplate, UserTemplateCreate, UserTemplateUpdate
from backend.utils.file_ops import PDFGenerator, save_pdf, extract_text_from_pdf
from backend.utils.path_ops import create_new_application_path, get_current_application_path
from backend.models import db_models
from backend.models.db import get_db

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("/resume/plain")
def generate_tailored_plain_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    # Get user preferences if they exist
    user_preferences = None
    preferences = db.query(db_models.UserPreferences).filter(db_models.UserPreferences.user_id == current_user.id).first()
    if preferences:
        user_preferences = preferences.preferences_text

    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    return ai_service.generate_tailored_resume_text(
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template,
        user_preferences
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
    
    # Save the plain text version for future editing
    text_file_path = os.path.join(save_path, "CoverLetter.txt")
    with open(text_file_path, 'w') as f:
        f.write(cover_letter_text)
    
    # Generate PDF
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
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
    return FileResponse(
        path=pdf_file_path,
        filename=f"{current_user.username}_{timestamp}_{company_name}_cover_letter.pdf",
        media_type="application/pdf"
    )

@router.get("/resume/pdf", response_class=FileResponse)
async def generate_and_save_pdf_resume(
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
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
    
    # Get user preferences if they exist
    user_preferences = None
    preferences = db.query(db_models.UserPreferences).filter(db_models.UserPreferences.user_id == current_user.id).first()
    if preferences:
        user_preferences = preferences.preferences_text
    
    company_name = ai_service.get_company_name(job_description)
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
    save_path = create_new_application_path(current_user.username, company_name, timestamp)
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    latex_compiler_response, _, structured_resume_json = await ai_service.generate_structured_latex_resume_async(
        str(save_path),
        current_user.resumes.resume_content,
        job_description,
        tailoring_options.ai_model,
        tailoring_options.resume_template,
        user_preferences,
        current_user.id,
        db
    )
    
    pdf_file_path = save_pdf(str(save_path), latex_compiler_response.content, current_user.username)
    
    # Store the structured resume JSON for later use in the session or a temporary file
    # This would be better implemented with a proper session or database storage
    json_file_path = os.path.join(save_path, "resume.json")
    with open(json_file_path, 'w') as f:
        f.write(structured_resume_json)
    
    structured_resume = json.loads(structured_resume_json)
    name = structured_resume.get('personal_info', {}).get('name', '') if structured_resume.get('personal_info', {}).get('name') else ''
    # Return the PDF file directly
    return FileResponse(
        path=pdf_file_path,
        filename=f"{name}_{timestamp}_{company_name}.pdf",
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
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
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
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
    anonymous_username = f"anonymous_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    # Create a save path
    save_path = create_new_application_path(anonymous_username, "improved_resume")

    tailoring_options = TailoringOptionsBase()
    
    # Generate improved resume using AI with default options
    latex_compiler_response, _, _ = await ai_service.generate_structured_latex_resume_async(
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
    job_description: str = Query(..., description="The job description to tailor the resume for"),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a resume JSON based on free-form text instructions and return the updated PDF"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details first."
        )
    
    # Get the original resume content from the user's profile
    original_resume_content = current_user.resumes.resume_content
    
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
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
    new_save_path = create_new_application_path(current_user.username, company_name, timestamp)
    
    # Get user's tailoring options
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    # Get user preferences if they exist
    user_preferences = None
    preferences = db.query(db_models.UserPreferences).filter(db_models.UserPreferences.user_id == current_user.id).first()
    if preferences:
        user_preferences = preferences.preferences_text
    
    try:
        # Process the edit and generate PDF using the new service function
        latex_compiler_response, updated_resume_json = ai_service.update_resume_with_instructions(
            last_resume_json,
            job_description,
            edit_instruction,
            str(new_save_path),
            AIModel.gpt_4_1_nano,  # Use GPT-4.1 Nano model
            tailoring_options.resume_template,  # Use user's template preference
            current_user.id,
            db
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

@router.get("/cover-letter/edit", response_class=FileResponse)
async def edit_cover_letter_with_instructions(
    edit_instruction: str = Query(..., description="Free-form text instructions for editing the cover letter"),
    job_description: str = Query(..., description="The job description to tailor the cover letter for"),
    current_user = Depends(get_current_user)
):
    """Update a cover letter based on free-form text instructions and return the updated PDF"""
    # Get the current application path to read the existing cover letter
    current_save_path = get_current_application_path(current_user.username)
    
    # Check if the cover letter file exists
    cover_letter_file_path = os.path.join(current_save_path, "CoverLetter.pdf")
    
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details first."
        )
    
    if not os.path.exists(cover_letter_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter found. Please generate a cover letter first."
        )
    
    # Check if we have the plain text cover letter
    text_file_path = os.path.join(current_save_path, "CoverLetter.txt")
    
    # If we don't have the text file, create it with an error message
    if not os.path.exists(text_file_path):
        # We need the original cover letter text to edit it
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cover letter text not found. Please generate a new cover letter."
        )
    
    # Read the cover letter text
    with open(text_file_path, 'r') as f:
        cover_letter_text = f.read()
    
    # Create a new path for the updated cover letter with a timestamp
    company_name = os.path.basename(current_save_path).split('_')[-1]
    timestamp = datetime.now().strftime("%m-%d_%H-%M")
    new_save_path = create_new_application_path(current_user.username, company_name, timestamp)
    
    try:
        # Process the edit using the AI service
        updated_cover_letter = ai_service.update_cover_letter_with_instructions(
            cover_letter_text,
            current_user.resumes.resume_content,  # Pass the user's resume content
            job_description,  # Pass the job description
            edit_instruction
        )
        
        # Save the updated cover letter text
        new_text_file_path = os.path.join(new_save_path, "CoverLetter.txt")
        with open(new_text_file_path, 'w') as f:
            f.write(updated_cover_letter)
        
        # Generate a PDF from the updated cover letter
        pdf_generator = PDFGenerator()
        pdf_generator.create_pdf_document(
            updated_cover_letter,
            output_folder=str(new_save_path),
        )
        
        # The path to the newly generated PDF
        new_pdf_file_path = os.path.join(new_save_path, "CoverLetter.pdf")
        
        # Return the PDF file
        return FileResponse(
            path=new_pdf_file_path,
            filename=f"{current_user.username}_{timestamp}_{company_name}_updated_cover_letter.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update cover letter: {str(e)}"
        )

@router.get("/cover-letter/text", response_class=PlainTextResponse)
def get_cover_letter_text_content(
    current_user = Depends(get_current_user)
):
    """Get the raw content of the cover letter text file"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume"
        )
    
    # Get the current application path for this user
    save_path = get_current_application_path(current_user.username)
    
    # Check if the text file exists
    text_file_path = os.path.join(save_path, "CoverLetter.txt")
    
    if not os.path.exists(text_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cover letter text file found. Please generate a cover letter first."
        )
    
    # Read the content of the file
    with open(text_file_path, 'r') as f:
        text_content = f.read()
    
    # Return the raw content
    return text_content

@router.get("/questions/answer/edit")
def edit_answer_with_instructions(
    edit_instruction: str = Query(..., description="Instructions for editing the answer"),
    original_answer: str = Query(..., description="The original answer to edit"),
    job_description: str = Query(..., description="The job description context"),
    question: str = Query(..., description="The question being answered"),
    current_user = Depends(get_current_user)
) -> str:
    """Update an application answer based on free-form text instructions"""
    if not current_user.resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a resume record. Please upload a resume first."
        )
    
    # Check if the user has resume content
    if not current_user.resumes.resume_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No resume content found. Please add your resume details first."
        )
    
    tailoring_options = current_user.tailoring_options or TailoringOptionsBase()
    
    try:
        # Process the edit using the AI service
        updated_answer = ai_service.update_answer_with_instructions(
            original_answer,
            question,
            job_description,
            current_user.resumes.resume_content,  # Pass the user's resume content
            edit_instruction,
            tailoring_options.ai_model
        )
        
        # Get the current application path for this user
        save_path = get_current_application_path(current_user.username)
        
        # Save the Q&A pair in the application folder
        qa_file_path = os.path.join(save_path, f"question_updated_{datetime.now().strftime('%m%d_%H%M')}.txt")
        with open(qa_file_path, 'w') as f:
            f.write(f"Question: {question}\n\nAnswer: {updated_answer}\n\nEdit Instructions: {edit_instruction}")
        
        return updated_answer
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update answer: {str(e)}"
        )

# Template Management Endpoints

@router.post("/templates", response_model=UserTemplate)
def create_user_template(
    template: UserTemplateCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new personalized LaTeX template for the user"""
    
    # Validate LaTeX compiler
    valid_compilers = ["pdflatex", "xelatex", "lualatex"]
    if template.compiler not in valid_compilers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid compiler. Must be one of: {valid_compilers}"
        )
    
    # Optional: Validate LaTeX template by testing compilation
    # This would require a more complex validation system
    
    # Create the template
    db_template = db_models.UserTemplate(
        user_id=current_user.id,
        name=template.name,
        latex_content=template.latex_content,
        compiler=template.compiler,
        is_active=template.is_active
    )
    
    # If this template is set as active, deactivate others
    if template.is_active:
        db.query(db_models.UserTemplate).filter(
            db_models.UserTemplate.user_id == current_user.id,
            db_models.UserTemplate.id != db_template.id
        ).update({"is_active": False})
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return db_template

@router.get("/templates", response_model=list[UserTemplate])
def get_user_templates(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all templates for the current user"""
    templates = db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.user_id == current_user.id
    ).order_by(db_models.UserTemplate.created_at.desc()).all()
    
    return templates

@router.get("/templates/{template_id}", response_model=UserTemplate)
def get_user_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template by ID"""
    template = db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.id == template_id,
        db_models.UserTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template

@router.put("/templates/{template_id}", response_model=UserTemplate)
def update_user_template(
    template_id: int,
    template_update: UserTemplateUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific template"""
    template = db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.id == template_id,
        db_models.UserTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Validate compiler if provided
    if template_update.compiler:
        valid_compilers = ["pdflatex", "xelatex", "lualatex"]
        if template_update.compiler not in valid_compilers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid compiler. Must be one of: {valid_compilers}"
            )
    
    # Update fields
    update_data = template_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    # If this template is being set as active, deactivate others
    if template_update.is_active:
        db.query(db_models.UserTemplate).filter(
            db_models.UserTemplate.user_id == current_user.id,
            db_models.UserTemplate.id != template_id
        ).update({"is_active": False})
    
    db.commit()
    db.refresh(template)
    
    return template

@router.delete("/templates/{template_id}")
def delete_user_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific template"""
    template = db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.id == template_id,
        db_models.UserTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}

@router.post("/templates/{template_id}/activate")
def activate_user_template(
    template_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Activate a specific template (deactivates all others)"""
    template = db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.id == template_id,
        db_models.UserTemplate.user_id == current_user.id
    ).first()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Deactivate all other templates
    db.query(db_models.UserTemplate).filter(
        db_models.UserTemplate.user_id == current_user.id
    ).update({"is_active": False})
    
    # Activate the selected template
    template.is_active = True
    db.commit()
    
    return {"message": "Template activated successfully"} 