from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        Index('ix_books_author_genre', 'author', 'genre'),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    genre = Column(String, index=True)
    year_published = Column(Integer)
    summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships - cascade delete reviews when book is deleted
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
