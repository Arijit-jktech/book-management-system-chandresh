from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import logging
from app.core import database
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, Book as BookSchema
from app.api import deps

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new book (requires authentication)."""
    try:
        book = Book(**book_in.model_dump())
        db.add(book)
        await db.commit()
        await db.refresh(book)
        logger.info(f"Book created: {book.title} (ID: {book.id}) by user {current_user.email}")
        return book
    except Exception as e:
        logger.error(f"Error creating book: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the book"
        )

@router.get("/", response_model=List[BookSchema])
async def read_books(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db)
):
    """Get list of books (public endpoint)."""
    try:
        # Validate pagination parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000"
            )
        
        result = await db.execute(select(Book).offset(skip).limit(limit))
        books = result.scalars().all()
        return books
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching books: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching books"
        )

@router.get("/{book_id}", response_model=BookSchema)
async def read_book(
    book_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """Get a specific book by ID (public endpoint)."""
    try:
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book {book_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the book"
        )

@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update a book (requires authentication)."""
    try:
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        
        update_data = book_in.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        for field, value in update_data.items():
            setattr(book, field, value)
        
        db.add(book)
        await db.commit()
        await db.refresh(book)
        logger.info(f"Book updated: {book.title} (ID: {book.id}) by user {current_user.email}")
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating book {book_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the book"
        )

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a book (requires authentication). Reviews will be cascade deleted."""
    try:
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        
        # Use proper SQLAlchemy delete
        await db.execute(delete(Book).where(Book.id == book_id))
        await db.commit()
        logger.info(f"Book deleted: ID {book_id} by user {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting book {book_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the book"
        )
