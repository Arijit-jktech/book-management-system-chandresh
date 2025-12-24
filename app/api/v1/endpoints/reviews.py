from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import logging
from app.core import database
from app.models.review import Review
from app.models.book import Book
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, Review as ReviewSchema
from app.api import deps

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Create a new review for a book (requires authentication)."""
    try:
        # Verify book exists
        result = await db.execute(select(Book).where(Book.id == review_in.book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {review_in.book_id} not found"
            )
        
        # Create review
        review = Review(
            **review_in.model_dump(),
            user_id=current_user.id
        )
        db.add(review)
        await db.commit()
        await db.refresh(review)
        logger.info(f"Review created for book {review.book_id} by user {current_user.email}")
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the review"
        )

@router.get("/book/{book_id}", response_model=List[ReviewSchema])
async def get_book_reviews(
    book_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db)
):
    """Get all reviews for a specific book (public endpoint)."""
    try:
        # Verify book exists
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalars().first()
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        
        # Get reviews
        result = await db.execute(
            select(Review)
            .where(Review.book_id == book_id)
            .offset(skip)
            .limit(limit)
        )
        reviews = result.scalars().all()
        return reviews
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reviews for book {book_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching reviews"
        )

@router.get("/{review_id}", response_model=ReviewSchema)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    """Get a specific review by ID (public endpoint)."""
    try:
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalars().first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with ID {review_id} not found"
            )
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching review {review_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching the review"
        )

@router.put("/{review_id}", response_model=ReviewSchema)
async def update_review(
    review_id: int,
    review_in: ReviewUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Update a review (requires authentication and ownership)."""
    try:
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalars().first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with ID {review_id} not found"
            )
        
        # Check ownership - users can only edit their own reviews
        if review.user_id != current_user.id:
            logger.warning(f"User {current_user.email} attempted to edit review {review_id} owned by user {review.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own reviews"
            )
        
        update_data = review_in.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        for field, value in update_data.items():
            setattr(review, field, value)
        
        db.add(review)
        await db.commit()
        await db.refresh(review)
        logger.info(f"Review {review_id} updated by user {current_user.email}")
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review {review_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the review"
        )

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete a review (requires authentication and ownership)."""
    try:
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalars().first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review with ID {review_id} not found"
            )
        
        # Check ownership - users can only delete their own reviews
        if review.user_id != current_user.id:
            logger.warning(f"User {current_user.email} attempted to delete review {review_id} owned by user {review.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )
        
        await db.execute(delete(Review).where(Review.id == review_id))
        await db.commit()
        logger.info(f"Review {review_id} deleted by user {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review {review_id}: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the review"
        )
