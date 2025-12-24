from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range_check'),
    )

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
