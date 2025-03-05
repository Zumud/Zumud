from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from backend.models.db import get_db
from backend.models.user_models import User, UserCreate
from backend.models.resume_models import Resume
from backend.models.legal_authorization_models import LegalAuthorization
from backend.models import db_models
from backend.api.auth import get_current_user, pwd_context
from backend.models.tailoring_options import TailoringOptionsBase, TailoringOptions

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=User)
def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
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
    
    if user.initial_resume:
        db_resume = db_models.Resume(
            user_id=db_user.id,
            resume_content=user.initial_resume
        )
        db.add(db_resume)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me/resume", response_model=Resume)
def get_user_resume(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user's resume"""
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {current_user.id} does not have a resume"
        )
    return resume

@router.put("/me/resume", response_model=Resume)
def update_resume(resume_content: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update current user's resume"""
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume found to update"
        )
    
    resume.resume_content = resume_content
    resume.last_updated = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(resume)
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