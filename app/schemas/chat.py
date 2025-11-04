import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.message import LastMessagePreview, MessageOut
from app.schemas.user import UserPublic


class ChatPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    avatar: Optional[str] = None
    is_group: bool
    last_message: Optional[LastMessagePreview] = None


class ChatDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_group: bool
    name: Optional[str] = None
    avatar: Optional[str] = None
    users: List[UserPublic]


class ChatWithMessagesPage(BaseModel):
    chat: ChatDetail
    messages: list[MessageOut]
    total: int
    limit: int
    offset: int


