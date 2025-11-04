import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(examples=["jane@example.com"])
    username: str = Field(min_length=3, max_length=50, examples=["jane_doe"])
    password: str = Field(min_length=8, max_length=256, examples=["StrongPassword123!"])
    first_name: Optional[str] = Field(default=None, examples=["Jane"])
    last_name: Optional[str] = Field(default=None, examples=["Doe"])
    avatar: Optional[str] = Field(default=None, examples=["https://example.com/avatar.jpg"])


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    last_seen: Optional[datetime] = None


class UserSearchPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None


