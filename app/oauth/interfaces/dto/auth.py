from pydantic import BaseModel, EmailStr, HttpUrl, validator
from typing import Optional

class UserCreateDTO(BaseModel):
    """DTO for creating a new user"""
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name cannot exceed 255 characters')
        return v.strip()

class GoogleAuthDTO(BaseModel):
    """DTO for Google OAuth authentication"""
    access_token: str
    id_token: Optional[str] = None

class EmailAuthDTO(BaseModel):
    """DTO for email-based authentication"""
    email: EmailStr
    name: str
    picture: Optional[str] = None

class AuthResponseDTO(BaseModel):
    """DTO for authentication response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserResponseDTO(BaseModel):
    """DTO for user data response"""
    id: int
    email: str
    name: str
    picture: Optional[str] = None
    google_id: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True
