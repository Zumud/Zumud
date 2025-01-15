from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database.db import get_db
from backend.models import tables
from backend.utils import hash
from backend.utils import oauth2
from backend.models import user_models, resume_models
from datetime import datetime, timezone
from loguru import logger

auth_router = APIRouter()
@auth_router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(tables.User).filter(tables.User.username==user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not hash.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    access_token = oauth2.create_access_token(data={'user_id':user.id})
    return {"access_token": access_token, "token_type":"bearer", "username": user.username,
        "user_id": user.id}

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: user_models.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(tables.User).filter(tables.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
   # Hash the password
    hashed_password = hash.hashing(user.password)
    db_user = tables.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.flush()  # This gets the user.id without committing
    
    # Create resume if provided
    if user.initial_resume:
        db_resume = tables.Resume(
            user_id=db_user.id,
            resume_content=user.initial_resume
        )
        db.add(db_resume)
    
    db.commit()
    db.refresh(db_user)

    return user_models.User.model_validate(db_user)

@auth_router.get(f"/user/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(tables.User).filter(tables.User.id == id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'user with id {id} does not exist')

@auth_router.get("/get_resume")   
def get_user_resume(db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
    """Get user's resume"""
    resume = db.query(tables.Resume)\
        .filter(tables.Resume.user_id == current_user.id)\
        .first()
    
    if resume:
        return resume_models.Resume.model_validate(resume)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'user with id {current_user.id} does not have resume')

@auth_router.put("/update_resume")
def update_resume(resume: resume_models.ResumeBase, db: Session = Depends(get_db), current_user = Depends(oauth2.get_current_user)):
        """Update or create user's resume"""
        # Check if user has a resume
        updated_resume = db.query(tables.Resume).filter(tables.Resume.user_id == current_user.id).first()
        
        
        
        if not updated_resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"There is no resume to become updated")
        
        # Update existing resume
        updated_resume.resume_content = resume.resume_content
        updated_resume.last_updated = datetime.now(timezone.utc)
        
        
        db.commit()
        db.refresh(updated_resume)
        return updated_resume

