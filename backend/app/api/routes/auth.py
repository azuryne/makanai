from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, or_
from datetime import timedelta

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    UserResponse,
    LoginRequest,
    Token
)
from app.api.deps import get_current_user
from app.config import settings
from app.services.auth import verify_password, create_access_token, hash_password

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user"""

    # Check if email already exist
    result = await db.execute(
        select(User).where(
                User.email == request.email,
        )
    )
    existing_user = result.scalar_one_or_none()  # return data if matched, none if no match 

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User with this email or username already exists"
        )
    
    # Create new user 
    new_user = User(
        email = request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)  # response_model : to convert database object into object that matches the 'Token'
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token"""

    # Find user by email or username
    result = await db.execute(
        select(User).where(
                User.email == login_data.email
        )
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password are correct 
    if not user or not verify_password(login_data.password, user.hashed_password):   # Hashed password is from database
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Check if user is active 
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # Create JWT token 
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(
        access_token=access_token
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user info"""
    return current_user