from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Book Management System"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "llama-3.3-70b-versatile"  # Updated to current Groq model

    class Config:
        env_file = ".env"

settings = Settings()
