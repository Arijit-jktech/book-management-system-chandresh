from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import database
from app.models.review import Review
from app.models.book import Book
from app.models.user import User
from app.schemas.review import ReviewCreate, Review as ReviewSchema
from app.api import deps

router = APIRouter()

@router.post("/books/{book_id}/reviews", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review_in: ReviewCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Check if book exists
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    review = Review(
        **review_in.model_dump(),
        book_id=book_id,
        user_id=current_user.id
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review

@router.get("/books/{book_id}/reviews", response_model=List[ReviewSchema])
async def read_reviews(
    book_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(Review).where(Review.book_id == book_id))
    reviews = result.scalars().all()
    return reviews
