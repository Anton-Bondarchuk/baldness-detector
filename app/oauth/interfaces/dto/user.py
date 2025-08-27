from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class UserDTO(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: Optional[str] = None
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError('Name cannot be empty')
        if len(v) > 255:
            raise ValueError('Name cannot exceed 255 characters')
        return v.strip()