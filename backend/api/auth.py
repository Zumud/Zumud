from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config.envs import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from backend.models.db import get_db
from backend.models import resume_models, db_models, user_models

auth_router = APIRouter(tags=["authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')  # OAuth2 scheme for token-based authentication using /login endpoint
    
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : int = int(payload.get("user_id"))
        user = db.query(db_models.User).filter(db_models.User.id==id).first()
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
    user = db.query(db_models.User).filter(db_models.User.username==user_credentials.username).first()
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
