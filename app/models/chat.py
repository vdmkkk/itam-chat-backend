import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Chat(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    is_group: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    users = relationship(
        "User",
        secondary="chatuser",
        back_populates="chats",
        lazy="selectin",
    )

    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all,delete-orphan",
        lazy="selectin",
        order_by="desc(Message.created_at)",
    )


class ChatUser(Base):
    """Association table for Chat<->User."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Optional backrefs are not necessary; relationships already defined on Chat and User


