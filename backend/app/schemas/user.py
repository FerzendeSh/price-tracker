from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    email_verified: bool = False
    is_admin: bool = False

    class Config:
        from_attributes = True


class AdminUserRead(BaseModel):
    """Extended user info visible to admins."""
    id: int
    username: str
    email: EmailStr
    email_verified: bool = False
    is_admin: bool = False
    product_count: int = 0

    class Config:
        from_attributes = True

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

class LoginRequest(BaseModel):
    username: str
    password: str = Field(min_length=8, max_length=72)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
