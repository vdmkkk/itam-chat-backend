import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserPublic


router = APIRouter(prefix="", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with unique email and username.",
)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserPublic:
    # Check uniqueness
    existing = await db.execute(
        select(User).where(or_(User.email == payload.email, User.username == payload.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email or username already in use")

    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        avatar=payload.avatar,
        last_seen=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserPublic.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and receive a JWT",
    description=(
        "Authenticate with username or email and password. Returns a Bearer JWT. "
        "In DEV mode tokens have no expiration; in production they expire after the configured TTL."
    ),
)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    q = await db.execute(
        select(User).where(or_(User.email == payload.username_or_email, User.username == payload.username_or_email))
    )
    user = q.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


