import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageSeenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID = Field(description="User who has seen the message")
    seen_at: datetime


class MessageCreate(BaseModel):
    text_content: Optional[str] = Field(default=None, max_length=4000, examples=["Hello!"])
    image_content: Optional[str] = Field(default=None, examples=["https://example.com/image.png"])


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chat_id: uuid.UUID
    from_user_id: uuid.UUID
    text_content: Optional[str] = None
    image_content: Optional[str] = None
    created_at: datetime
    seen_by: List[MessageSeenOut] = []


class LastMessagePreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_user_id: uuid.UUID
    text_content: Optional[str] = None
    image_content: Optional[str] = None
    created_at: datetime


