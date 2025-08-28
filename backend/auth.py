# utils/auth.py
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_db
from models import User

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")  # production nên random + env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: AsyncSession):
    """Decode JWT token, return User object or raise exception"""
    from fastapi import HTTPException, status

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = db.execute(select(User).where(User.email == email))
    return result.scalars().first()

def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

def create_user(db: AsyncSession, email: str, password: str, full_name: Optional[str] = None) -> User:
    hashed_pw = hash_password(password)
    user = User(email=email, hashed_password=hashed_pw, full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  # token endpoint

def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    return verify_token(token, db)
