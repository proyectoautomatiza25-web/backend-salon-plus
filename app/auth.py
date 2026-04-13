from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database, models, schemas
import os

# CONFIG
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey_dev_only_change_in_prod")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60 # 30 days for easy dev

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_password(plain_password, hashed_password):
    # Fix: Truncate to 72 bytes for bcrypt compatibility
    password_bytes = plain_password.encode('utf-8')
    plain_password = password_bytes[:72] if len(password_bytes) > 72 else plain_password
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # Fix: Truncate to 72 bytes for bcrypt compatibility
    password_bytes = password.encode('utf-8') if isinstance(password, str) else password
    password = password_bytes[:72] if len(password_bytes) > 72 else password
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def check_subscription_active(current_user: models.User = Depends(get_current_user)):
    # TEMPORARY: Allow all users to bypass expiry check for testing
    return current_user
