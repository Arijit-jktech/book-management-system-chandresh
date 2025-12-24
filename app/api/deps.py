from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.core import security, config, database
from app.models.user import User
from app.schemas.token import TokenData

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config.settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(database.get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing 'sub' claim")
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalars().first()
    if user is None:
        logger.warning(f"User not found for email: {token_data.email}")
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user has admin role.
    Use this for admin-only endpoints.
    """
    if current_user.role != "admin":
        logger.warning(f"Non-admin user {current_user.email} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user
