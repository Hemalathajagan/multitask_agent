from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.db.database import get_db
from app.db.crud import (
    create_user, get_user_by_email, get_user_by_username,
    update_user_profile, update_user_password, update_user_photo
)
from app.auth.security import verify_password, get_password_hash, create_access_token
from app.auth.dependencies import get_current_user
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserProfileUpdate, PasswordChange, ProfilePhotoUpdate
from app.config import get_settings
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_username = await get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = await create_user(db, user_data.email, user_data.username, hashed_password)

    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    user = await get_user_by_email(db, user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )

    return Token(access_token=access_token)


@router.post("/logout")
async def logout(response: Response):
    """Logout and clear access token cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    # Check if new username is taken
    if profile_data.username and profile_data.username != current_user.username:
        existing = await get_user_by_username(db, profile_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Check if new email is taken
    if profile_data.email and profile_data.email != current_user.email:
        existing = await get_user_by_email(db, profile_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    user = await update_user_profile(
        db,
        current_user.id,
        username=profile_data.username,
        email=profile_data.email
    )

    return user


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check new passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )

    # Check new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )

    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    await update_user_password(db, current_user.id, hashed_password)

    return {"message": "Password changed successfully"}


@router.put("/photo", response_model=UserResponse)
async def update_profile_photo(
    photo_data: ProfilePhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile photo."""
    user = await update_user_photo(db, current_user.id, photo_data.profile_photo)
    return user
