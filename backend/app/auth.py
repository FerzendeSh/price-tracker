from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from app.db import get_user_by_username


SECRET_KEY = "3fbffe28c0b3dcf635f25634e6870008071ec51a240028884c22e418ed340612"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# configuration
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password : str) -> str:
    return bcrypt_context.hash(password)

def verify_password(password : str, hashed_password : str) -> bool:
    return bcrypt_context.verify(password, hashed_password)


def create_access_token(*, subject : str, expires_minutes : int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM) 
    

def get_current_user(token : str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : Optional[str] = payload.get("sub")
        
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_username(username)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

