from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    genre: Optional[str] = None
    year_published: Optional[int] = None
    summary: Optional[str] = None
    
    @field_validator('title', 'author')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Field must be at least 2 characters long')
        return v.strip()
    
    @field_validator('year_published')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 1000 or v > 2100:
                raise ValueError('Year must be between 1000 and 2100')
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    year_published: Optional[int] = None
    summary: Optional[str] = None
    
    @field_validator('title', 'author')
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Field cannot be empty')
            if len(v.strip()) < 2:
                raise ValueError('Field must be at least 2 characters long')
            return v.strip()
        return v
    
    @field_validator('year_published')
    @classmethod
    def validate_year(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 1000 or v > 2100:
                raise ValueError('Year must be between 1000 and 2100')
        return v

class Book(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
