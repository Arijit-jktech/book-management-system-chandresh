from datetime import datetime, timedelta
from typing import Optional, Any, Union
import re
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Using argon2 instead of bcrypt due to compatibility issues
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ALGORITHM = settings.ALGORITHM

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def validate_email(email: str) -> bool:
    """
    Validate email format using regex.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email format is valid, False otherwise
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, ""
