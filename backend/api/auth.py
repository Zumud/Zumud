from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config.envs import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from backend.database.db import get_db
from backend.models import resume_models, tables, user_models

auth_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')  # OAuth2 scheme for token-based authentication using /login endpoint
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : int = int(payload.get("user_id"))
        user = db.query(tables.User).filter(tables.User.id==id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing user ID in token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user

@auth_router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(tables.User).filter(tables.User.username==user_credentials.username).first()
    if not user or not pwd_context.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")  # For security reasons, don't specify the reason for failure
    
    # Create access token
    token_expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {'user_id':user.id, 'exp': token_expiration}    
    access_token = jwt.encode(token_data, key=SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer", "username": user.username, "user_id": user.id}

@auth_router.post("/logout")
def logout():
    # Logout is a no-op in this implementation
    return {"message": "Logged out successfully"}

@auth_router.get(f"/user")
def get_user(current_user: dict = Depends(get_current_user)):
    return current_user

@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: user_models.UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    if db.query(tables.User).filter(tables.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
   # Hash the password
    hashed_password = pwd_context.hash(user.password)
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
 
@auth_router.get("/get_resume")   
def get_user_resume(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's resume"""
    resume = db.query(tables.Resume)\
        .filter(tables.Resume.user_id == current_user.id)\
        .first()
    
    if resume:
        return resume_models.Resume.model_validate(resume)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f'user with id {current_user.id} does not have resume')

@auth_router.put("/update_resume")
def update_resume(resume: resume_models.ResumeBase, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
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

