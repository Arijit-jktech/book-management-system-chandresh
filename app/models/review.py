from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    review_text = Column(Text)
    rating = Column(Integer)

    book = relationship("Book", back_populates="reviews")
    user = relationship("User")
