import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(json_schema_extra={"example": "jane@example.com"})
    username: str = Field(min_length=3, max_length=50, json_schema_extra={"example": "jane_doe"})
    password: str = Field(min_length=8, max_length=256, json_schema_extra={"example": "StrongPassword123!"})
    first_name: Optional[str] = Field(default=None, json_schema_extra={"example": "Jane"})
    last_name: Optional[str] = Field(default=None, json_schema_extra={"example": "Doe"})
    avatar: Optional[str] = Field(default=None, json_schema_extra={"example": "https://example.com/avatar.jpg"})


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


