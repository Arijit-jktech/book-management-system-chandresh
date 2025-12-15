from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    genre = Column(String, index=True)
    year_published = Column(Integer)
    summary = Column(Text)

    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")
