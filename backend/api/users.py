from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from backend.models.db import get_db
from backend.models import db_models, user_models, resume_models
from backend.api.auth import pwd_context, get_current_user

user_router = APIRouter(tags=["users"])

@user_router.get("/user")
def get_user(current_user: dict = Depends(get_current_user)):
    return current_user

@user_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: user_models.UserCreate, db: Session = Depends(get_db)):
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

    return user_models.User.model_validate(db_user)

@user_router.get("/get_resume")
def get_user_resume(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's resume"""
    resume = db.query(db_models.Resume)\
        .filter(db_models.Resume.user_id == current_user.id)\
        .first()
    
    if resume:
        return resume_models.Resume.model_validate(resume)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'user with id {current_user.id} does not have resume')

@user_router.put("/update_resume")
def update_resume(resume_content: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
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