from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    review_text: str
    rating: int
    
    @field_validator('review_text')
    @classmethod
    def validate_review_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Review text cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Review text must be at least 10 characters long')
        return v.strip()
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

class ReviewCreate(ReviewBase):
    book_id: int

class ReviewUpdate(BaseModel):
    review_text: Optional[str] = None
    rating: Optional[int] = None
    
    @field_validator('review_text')
    @classmethod
    def validate_review_text(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Review text cannot be empty')
            if len(v.strip()) < 10:
                raise ValueError('Review text must be at least 10 characters long')
            return v.strip()
        return v
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 1 or v > 5:
                raise ValueError('Rating must be between 1 and 5')
        return v

class Review(ReviewBase):
    id: int
    book_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
