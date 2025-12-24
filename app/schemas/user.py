from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        from app.core.security import validate_password_strength
        is_valid, error_msg = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

class UserUpdate(UserBase):
    password: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            from app.core.security import validate_password_strength
            is_valid, error_msg = validate_password_strength(v)
            if not is_valid:
                raise ValueError(error_msg)
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """User response model - never expose hashed_password"""
    pass
