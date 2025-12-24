from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.core import security, database
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(database.get_db)
):
    """Authenticate user and return access token."""
    try:
        result = await db.execute(select(User).where(User.email == form_data.username))
        user = result.scalars().first()
        
        if not user or not security.verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        logger.info(f"Successful login for user: {user.email}")
        access_token = security.create_access_token(subject=user.email)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(database.get_db)
):
    """Register a new user account."""
    try:
        # Validate email format (additional check beyond pydantic)
        if not security.validate_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_in.email))
        if result.scalars().first():
            logger.warning(f"Signup attempt with existing email: {user_in.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        # Create new user
        user = User(
            email=user_in.email,
            hashed_password=security.get_password_hash(user_in.password),
            role="user"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"New user created: {user.email}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )
