from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    message: str
    redirect_url: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool
    message: str
    error_code: Optional[str] = None
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str