from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger
import base64

from backend.models.db import get_db, SessionLocal
from backend.models.user_models import User, UserCreate, UserPreference, UserPreferenceCreate
from backend.models.resume_models import Resume, ResumeBase
from backend.models.legal_authorization_models import LegalAuthorization
from backend.models import db_models
from backend.api.auth import get_current_user, pwd_context
from backend.models.tailoring_options import TailoringOptionsBase, TailoringOptions
from backend.utils.file_utils import save_base64_pdf
from backend.utils.file_ops import extract_text_from_pdf
from backend.utils.resume_formatter import format_resume_text

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

async def process_resume_background(
    user_id: int, 
    resume_content: str,
):
    """Background task to process resume content and update the database"""
    # Create a new session for this background task
    db = SessionLocal()
    try:
        # Format resume content if it exists and isn't empty
        if resume_content and resume_content.strip():
            # Use the async format_resume_text function
            formatted_content = await format_resume_text(resume_content)
            
            # Update the resume record with formatted content
            db_resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == user_id).first()
            if db_resume:
                db_resume.resume_content = formatted_content
                db.commit()
    except Exception as e:
        logger.error(f"Error in background resume processing: {e}")
    finally:
        db.close()

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    """Create a new user account"""
    if db.query(db_models.User).filter(db_models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = pwd_context.hash(user.password)
    db_user = db_models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.flush()
    
    # Process resume text content and/or file
    resume_content = user.initial_resume
    resume_file_path = None
    
    # If PDF file is provided, extract text from it
    if user.resume_file:
        try:
            # Get the PDF content from base64
            if "base64," in user.resume_file:
                base64_data = user.resume_file.split("base64,")[1]
            else:
                base64_data = user.resume_file
                
            pdf_data = base64.b64decode(base64_data)
            
            # Extract text from the PDF
            extracted_text = await extract_text_from_pdf(pdf_data)
            
            # Use the extracted text as resume content if it's not empty
            if extracted_text and extracted_text.strip():
                resume_content = extracted_text
                
            # Still save the file for future reference but we won't expose API endpoints for it now
            resume_file_path = save_base64_pdf(user.resume_file)
        except Exception as e:
            # Log the error but continue with the signup process
            logger.error(f"Error extracting text from PDF: {e}")
    
    # Store initial unformatted content in the database
    db_resume = db_models.Resume(
        user_id=db_user.id,
        resume_content=resume_content or "",  # Store raw content initially
        resume_file_path=resume_file_path
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_user)
    
    # Schedule the resume formatting to happen in the background
    background_tasks.add_task(
        process_resume_background,
        db_user.id,
        resume_content,
    )
    
    return db_user

@router.get("/me/resume", response_model=Resume)
def get_user_resume(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's resume"""
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload or create a resume to get started."
        )
    return resume

@router.put("/me/resume", response_model=Resume)
def update_resume(
    resume_data: ResumeBase, 
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Update current user's resume"""
    
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found. Please upload or create a resume first."
        )
    
    # Get the updated content
    resume_content = resume_data.resume_content
    
    # Store unformatted content initially
    resume.resume_content = resume_content
    resume.last_updated = datetime.now(timezone.utc)
    
    db.commit()
    
    # Format the resume content in the background
    background_tasks.add_task(
        process_resume_background,
        current_user.id,
        resume_content,
    )
    
    
    return resume

@router.get("/me/work-authorization", response_model=LegalAuthorization)
def get_work_authorization(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's work authorization information"""
    legal_auth = db.query(db_models.LegalAuthorization).filter(db_models.LegalAuthorization.user_id == current_user.id).first()
    if not legal_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} does not have work authorization information"
        )
    return legal_auth

@router.put("/me/work-authorization", response_model=LegalAuthorization)
def update_work_authorization(work_authorization: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update current user's work authorization information"""
    legal_auth = db.query(db_models.LegalAuthorization).filter(db_models.LegalAuthorization.user_id == current_user.id).first()
    
    if legal_auth:
        legal_auth.work_authorization = work_authorization
        legal_auth.last_updated = datetime.now(timezone.utc)
    else:
        legal_auth = db_models.LegalAuthorization(
            user_id=current_user.id,
            work_authorization=work_authorization
        )
        db.add(legal_auth)
    
    db.commit()
    db.refresh(legal_auth)
    return legal_auth

@router.get("/me/tailoring-options", response_model=TailoringOptionsBase)
def get_tailoring_options(current_user = Depends(get_current_user)):
    """Get current user's tailoring options"""
    if not current_user.tailoring_options:
        return TailoringOptionsBase()
    return current_user.tailoring_options

@router.put("/me/tailoring-options", response_model=TailoringOptions)
def update_tailoring_options(tailoring_options: TailoringOptionsBase, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update current user's tailoring options"""
    db_tailoring_options = db.query(db_models.TailoringOptions).filter(db_models.TailoringOptions.user_id == current_user.id).first()
    
    if db_tailoring_options:
        db_tailoring_options.ai_model = tailoring_options.ai_model
        db_tailoring_options.resume_template = tailoring_options.resume_template
        db_tailoring_options.last_updated = datetime.now(timezone.utc)
    else:
        db_tailoring_options = db_models.TailoringOptions(
            user_id=current_user.id,
            ai_model=tailoring_options.ai_model,
            resume_template=tailoring_options.resume_template
        )
        db.add(db_tailoring_options)
    
    db.commit()
    db.refresh(db_tailoring_options)
    return db_tailoring_options

@router.post("/me/resume/upload", response_model=Resume)
async def upload_resume_pdf(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user), 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Upload a resume PDF to update the user's resume content"""
    start_time = datetime.now()
    logger.info(f"Starting resume upload for user {current_user.id}")
    
    # Check if file is PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Read the PDF contents
    pdf_contents = await file.read()
    
    # Extract text from PDF
    try:
        # Extract raw text from PDF
        resume_content = await extract_text_from_pdf(pdf_contents)
        
        if not resume_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF"
            )
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )
    
    # Save the PDF file
    resume_file_path = None
    try:
        # Convert to base64 for storage
        base64_data = base64.b64encode(pdf_contents).decode('utf-8')
        resume_file_path = save_base64_pdf(base64_data)
    except Exception as e:
        logger.error(f"Error saving PDF file: {e}")
        # Continue even if file save fails - we'll still update the text content
    
    # Check if user already has a resume
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    
    if resume:
        # Update existing resume with raw content
        resume.resume_content = resume_content
        resume.resume_file_path = resume_file_path or resume.resume_file_path
        resume.last_updated = datetime.now(timezone.utc)
    else:
        # Create new resume with raw content
        resume = db_models.Resume(
            user_id=current_user.id,
            resume_content=resume_content,
            resume_file_path=resume_file_path
        )
        db.add(resume)
    
    db.commit()
    
    # Format the resume content in the background
    background_tasks.add_task(
        process_resume_background,
        current_user.id,
        resume_content,
    )
    
    end_time = datetime.now()
    logger.info(f"Resume upload endpoint completed in {(end_time - start_time).total_seconds()} seconds")
    
    return resume

@router.get("/me/preferences", response_model=UserPreference)
def get_user_preferences(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's preferences"""
    preferences = db.query(db_models.UserPreferences).filter(db_models.UserPreferences.user_id == current_user.id).first()
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No preferences found for this user."
        )
    return preferences

@router.post("/me/preferences", response_model=UserPreference)
def add_user_preference(preference_data: UserPreferenceCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Add a new preference to the user's existing preferences"""
    # First, check if the user already has preference data
    preferences = db.query(db_models.UserPreferences).filter(db_models.UserPreferences.user_id == current_user.id).first()
    
    if preferences:
        # Append the new preference to existing preferences, separated by a newline
        if preferences.preferences_text:
            preferences.preferences_text += f"\n{preference_data.preference}"
        else:
            preferences.preferences_text = preference_data.preference
        
        preferences.last_updated = datetime.now(timezone.utc)
    else:
        # Create new preferences record
        preferences = db_models.UserPreferences(
            user_id=current_user.id,
            preferences_text=preference_data.preference
        )
        db.add(preferences)
    
    db.commit()
    db.refresh(preferences)
    return preferences
