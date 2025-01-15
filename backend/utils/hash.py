from passlib.context import CryptContext

# Using bcrypt for hashing the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashing(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)