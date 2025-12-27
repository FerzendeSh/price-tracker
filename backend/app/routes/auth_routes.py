from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.db import create_user, get_user_by_username
from app.auth import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username : str
    email : str
    password : str = Field(min_length=8, max_length=72)

class RegisterResponse(BaseModel):
    message: str
    username: str
    email: str
    
# Create the endpoint
@router.post("/register", response_model=RegisterResponse, status_code=201)
def register_user(data : RegisterRequest):
    hashed = hash_password(data.password)
    
    try:
        create_user(data.username, data.email, hashed)
        
    # Catch if the user already exists
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    
    # Otherwise
    return{
        "message": "User registered",
        "username" : data.username,
        "email" : data.email,
    }

class LoginRequest(BaseModel):
    username : str
    password : str = Field(min_length=8, max_length=72)

class LoginResponse(BaseModel):
    access_token : str
    token_type : str

@router.post("/login", response_model=LoginResponse, status_code=200)
def user_login(data : LoginRequest):
    user = get_user_by_username(data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # check the password
    if not verify_password(data.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Placeholder replace with JWT
    return{
        "access_token" : "fake-token",
        "token_type" : "bearer"
    }
