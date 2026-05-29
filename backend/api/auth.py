from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlalchemy.orm import Session

from backend.config.envs import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from backend.models.db import get_db
from backend.models import db_models

router = APIRouter(tags=["authentication"])

# Password hashing via pwdlib (maintained passlib replacement; unblocks bcrypt 5).
# bcrypt only considers the first 72 bytes of a password. passlib used to
# truncate silently; bcrypt 5 raises instead. We replicate the old truncation so
# (a) pre-existing bcrypt hashes still verify and (b) long passwords don't error.
_BCRYPT_MAX_BYTES = 72
_password_hasher = PasswordHash((BcryptHasher(),))


def _bcrypt_input(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


class _PasswordContext:
    """Drop-in replacement for the previous passlib CryptContext (.hash/.verify)."""

    @staticmethod
    def hash(password: str) -> str:
        return _password_hasher.hash(_bcrypt_input(password))

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        try:
            return _password_hasher.verify(_bcrypt_input(password), hashed_password)
        except Exception:
            return False


pwd_context = _PasswordContext()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = int(payload.get("user_id"))
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
            detail="Your session has expired. Please log in again to continue.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

@router.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.username==user_credentials.username).first()
    if not user or not pwd_context.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {'user_id': user.id, 'exp': token_expiration}    
    access_token = jwt.encode(token_data, key=SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.id
    }

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"} 