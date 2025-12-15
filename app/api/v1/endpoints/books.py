from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import database
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, Book as BookSchema
from app.api import deps

router = APIRouter()

@router.post("/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_in: BookCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    book = Book(**book_in.model_dump())
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

@router.get("/", response_model=List[BookSchema])
async def read_books(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(Book).offset(skip).limit(limit))
    books = result.scalars().all()
    return books

@router.get("/{book_id}", response_model=BookSchema)
async def read_book(
    book_id: int,
    db: AsyncSession = Depends(database.get_db)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_in: BookUpdate,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    update_data = book_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)
    
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(book)
    await db.commit()
    return None
