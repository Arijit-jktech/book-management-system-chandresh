from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core import database
from app.models.book import Book
from app.models.review import Review
from app.services import ai_service
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/generate-summary")
async def generate_summary(
    text: str = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_user)
):
    summary = await ai_service.generate_book_summary(text)
    return {"summary": summary}

@router.post("/books/{book_id}/generate-summary")
async def generate_and_save_book_summary(
    book_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Generate AI summary for a book and save it to the database."""
    # Get book
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Create text to summarize from book details
    text_to_summarize = f"Title: {book.title}\nAuthor: {book.author}"
    if book.genre:
        text_to_summarize += f"\nGenre: {book.genre}"
    if book.year_published:
        text_to_summarize += f"\nYear Published: {book.year_published}"
    
    # Generate summary using AI
    summary = await ai_service.generate_book_summary(text_to_summarize)
    
    # Save summary to database
    book.summary = summary
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    return {
        "id": book.id,
        "title": book.title,
        "summary": book.summary,
        "message": "Summary generated and saved successfully"
    }


@router.get("/books/{book_id}/summary")
async def get_book_summary_and_rating(
    book_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    # Get book
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Get aggregated rating
    rating_result = await db.execute(
        select(func.avg(Review.rating)).where(Review.book_id == book_id)
    )
    avg_rating = rating_result.scalar()
    
    return {
        "id": book.id,
        "title": book.title,
        "summary": book.summary,
        "average_rating": avg_rating or 0.0
    }

@router.get("/recommendations")
async def get_recommendations(
    db: AsyncSession = Depends(database.get_db),
    # current_user: User = Depends(deps.get_current_user) # Optional: personalize based on user
):
    # Simple recommendation logic: return top rated books
    # In a real system, this would use vector embeddings or user history
    stmt = (
        select(Book)
        .join(Review, Book.id == Review.book_id, isouter=True)
        .group_by(Book.id)
        .order_by(func.avg(Review.rating).desc().nulls_last())
        .limit(5)
    )
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books
