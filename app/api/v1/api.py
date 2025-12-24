from fastapi import APIRouter
from app.api.v1.endpoints import auth, books, reviews, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
