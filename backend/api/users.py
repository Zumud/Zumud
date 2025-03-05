from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from backend.models.db import get_db
from backend.models.user_models import User, UserCreate
from backend.models.resume_models import Resume
from backend.models.legal_authorization_models import LegalAuthorization
from backend.models import db_models
from backend.api.auth import pwd_context, get_current_user
from backend.models.tailoring_options import TailoringOptionsBase, TailoringOptions

user_router = APIRouter(tags=["user"])

@user_router.get("/user")
def get_user(current_user = Depends(get_current_user)):
    return current_user

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)) -> User:
    # Check if username already exists
    if db.query(db_models.User).filter(db_models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    db_user = db_models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.flush()  # This gets the user.id without committing
    
    # Create resume if provided
    if user.initial_resume:
        db_resume = db_models.Resume(
            user_id=db_user.id,
            resume_content=user.initial_resume
        )
        db.add(db_resume)
    
    db.commit()
    db.refresh(db_user)

    return db_user

@user_router.get("/get_resume")
def get_user_resume(current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> Resume:
    """Get user's resume"""
    resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    
    if resume:
        return resume
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'user with id {current_user.id} does not have resume')

@user_router.put("/update_resume")
def update_resume(resume_content: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> Resume:
    """Update or create user's resume"""
    # Check if user has a resume
    updated_resume = db.query(db_models.Resume).filter(db_models.Resume.user_id == current_user.id).first()
    
    if not updated_resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no resume to become updated")
    
    # Update existing resume
    updated_resume.resume_content = resume_content
    updated_resume.last_updated = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(updated_resume)
    return updated_resume

@user_router.get("/work_authorization")
def get_work_authorization(current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LegalAuthorization:
    """Get user's work authorization information"""
    legal_auth = db.query(db_models.LegalAuthorization).filter(db_models.LegalAuthorization.user_id == current_user.id).first()
    
    if legal_auth:
        return legal_auth
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'User with id {current_user.id} does not have work authorization information'
    )

@user_router.put("/work_authorization")
def update_work_authorization(work_authorization: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> LegalAuthorization:
    """Update or create user's work authorization information"""
    # Check if user has work authorization info
    legal_auth = db.query(db_models.LegalAuthorization).filter(db_models.LegalAuthorization.user_id == current_user.id).first()
    
    if legal_auth:
        # Update existing work authorization
        legal_auth.work_authorization = work_authorization
        legal_auth.last_updated = datetime.now(timezone.utc)
    else:
        # Create new work authorization
        legal_auth = db_models.LegalAuthorization(
            user_id=current_user.id,
            work_authorization=work_authorization
        )
        db.add(legal_auth)
    
    db.commit()
    db.refresh(legal_auth)
    return legal_auth

@user_router.get("/tailoring_options")
def get_tailoring_options(current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> TailoringOptionsBase:
    """Get user's tailoring options from database or return defaults"""
    if not current_user.tailoring_options:
        return TailoringOptionsBase()
    return current_user.tailoring_options

@user_router.put("/tailoring_options")
def update_tailoring_options(tailoring_options: TailoringOptionsBase, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> TailoringOptions:
    """Update or create user's tailoring options"""
    # Check if user has tailoring options
    db_tailoring_options = db.query(db_models.TailoringOptions).filter(db_models.TailoringOptions.user_id == current_user.id).first()
    
    if db_tailoring_options:
        # Update existing tailoring options
        db_tailoring_options.ai_model = tailoring_options.ai_model
        db_tailoring_options.resume_template = tailoring_options.resume_template
        db_tailoring_options.last_updated = datetime.now(timezone.utc)
    else:
        # Create new tailoring options
        db_tailoring_options = db_models.TailoringOptions(
            user_id=current_user.id,
            ai_model=tailoring_options.ai_model,
            resume_template=tailoring_options.resume_template
        )
        db.add(db_tailoring_options)
    
    db.commit()
    db.refresh(db_tailoring_options)
    return db_tailoring_options