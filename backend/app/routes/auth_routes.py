from pydantic import BaseModel
from fastapi import APIRouter


router = APIRouter(prefix="/auth", tags=["auth"])

# 1. Define what data you expect (schema)
# This tells FastAPI:
    # Expect JSON
    # Validate types
    # Reject bad requests automatically

class RegisterRequest(BaseModel):
    username : str
    email : str
    password : str

class RegisterResponse(BaseModel):
    message: str
    username: str
    email: str
    
# STEP 2. Create the endpoint (POST)

@router.post("/register", response_model=RegisterResponse)
def register_user(data : RegisterRequest):
    return{
        "message": "User registered",
        "username" : data.username,
        "email" : data.email,
    }

class LoginRequest(BaseModel):
    username : str
    password : str

class LoginResponse(BaseModel):
    access_token : str
    token_type : str

@router.post("/login", response_model=LoginResponse)
def user_login(data : LoginRequest):
    return{
        "username" : data.username,
    }
