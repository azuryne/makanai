from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class RegisterRequest(BaseModel):
    """Register Request or Request Schema: What frontend sends to backend (input)"""
    email: EmailStr
    # username: str = Field(..., min_length=3, max_length=50) # placeholder 
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str               #TODO: login using username
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None 

class UserResponse(BaseModel):
    id: UUID
    email: str 
    full_name: Optional[str]
    is_active: bool 
    created_at: datetime

    class Config:
        from_attributes = True