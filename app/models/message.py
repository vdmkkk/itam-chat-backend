import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Message(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    chat_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat.id", ondelete="CASCADE"))
    from_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))

    text_content: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
    image_content: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    chat = relationship("Chat", back_populates="messages")
    from_user = relationship("User")
    seen_by = relationship("MessageSeen", back_populates="message", cascade="all,delete-orphan", lazy="selectin")


class MessageSeen(Base):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("message.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), index=True)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    message = relationship("Message", back_populates="seen_by")
    user = relationship("User")

    __table_args__ = (
        UniqueConstraint("message_id", "user_id", name="uq_message_seen_message_user"),
    )


