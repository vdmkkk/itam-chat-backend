import uuid
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.config import PaginationParams
from app.db.session import get_db
from app.deps import get_current_user
from app.models.chat import Chat, ChatUser
from app.models.message import Message, MessageSeen
from app.models.user import User
from app.schemas.chat import ChatDetail, ChatPreview, ChatWithMessagesPage
from app.schemas.common import Page
from app.schemas.message import LastMessagePreview, MessageCreate, MessageOut
from app.schemas.user import UserPublic


router = APIRouter(prefix="/chats", tags=["Chats"])


def _other_user_name(users: List[User], me_id: uuid.UUID) -> tuple[str, str | None]:
    others = [u for u in users if u.id != me_id]
    if not others:
        return ("Unknown", None)
    other = others[0]
    full_name = " ".join([p for p in [other.first_name, other.last_name] if p])
    display_name = full_name or other.username
    return (display_name, other.avatar)


@router.get(
    "",
    response_model=Page[ChatPreview],
    summary="List chats for current user",
    description="Returns chat previews with last message. Supports pagination.",
)
async def list_chats(
    pagination: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Page[ChatPreview]:
    # Chats where current user is a member
    member_chats_sub = (
        select(Chat.id)
        .join(ChatUser, ChatUser.chat_id == Chat.id)
        .where(ChatUser.user_id == current_user.id)
        .subquery()
    )

    # Latest message per chat (created_at)
    latest_per_chat = (
        select(Message.chat_id, func.max(Message.created_at).label("max_created"))
        .where(Message.chat_id.in_(select(member_chats_sub.c.id)))
        .group_by(Message.chat_id)
        .subquery()
    )

    # Order chats by latest message desc (nulls last)
    chats_q = (
        select(Chat)
        .where(Chat.id.in_(select(member_chats_sub.c.id)))
        .join(latest_per_chat, Chat.id == latest_per_chat.c.chat_id, isouter=True)
        .order_by(desc(latest_per_chat.c.max_created.nulls_last()))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )

    total_q = select(func.count()).select_from(member_chats_sub)

    total_res, chats_res = await db.execute(total_q), await db.execute(chats_q)
    total = int(total_res.scalar() or 0)
    chats = chats_res.scalars().all()

    # Fetch users per chat (for computing names/avatars)
    users_res = await db.execute(
        select(ChatUser.chat_id, User)
        .join(User, User.id == ChatUser.user_id)
        .where(ChatUser.chat_id.in_([c.id for c in chats]))
    )
    users_by_chat: Dict[uuid.UUID, List[User]] = {}
    for chat_id, user in users_res.all():
        users_by_chat.setdefault(chat_id, []).append(user)

    # Fetch latest message entities
    latest_res = await db.execute(
        select(Message)
        .join(latest_per_chat, and_(Message.chat_id == latest_per_chat.c.chat_id, Message.created_at == latest_per_chat.c.max_created), isouter=True)
        .where(Message.chat_id.in_([c.id for c in chats]))
    )
    latest_by_chat: Dict[uuid.UUID, Message] = {m.chat_id: m for m in latest_res.scalars().all()}

    items: List[ChatPreview] = []
    for c in chats:
        display_name = c.name or ""
        display_avatar = c.avatar
        if not c.is_group:
            users = users_by_chat.get(c.id, [])
            display_name, display_avatar = _other_user_name(users, current_user.id)
        lm = latest_by_chat.get(c.id)
        last_message = (
            LastMessagePreview.model_validate(lm) if lm else None
        )
        items.append(
            ChatPreview(
                id=c.id,
                is_group=c.is_group,
                name=display_name,
                avatar=display_avatar,
                last_message=last_message,
            )
        )

    return Page[ChatPreview](items=items, total=total, limit=pagination.limit, offset=pagination.offset)


@router.get(
    "/{chat_id}",
    response_model=ChatWithMessagesPage,
    summary="Get chat details and messages",
    description="Returns chat details and paginated messages (newest first).",
)
async def get_chat(
    chat_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: Annotated[int, Query(20, ge=1, le=100)] = 20,
    offset: Annotated[int, Query(0, ge=0)] = 0,
) -> ChatWithMessagesPage:
    # Ensure membership
    member = await db.execute(
        select(ChatUser).where(ChatUser.chat_id == chat_id, ChatUser.user_id == current_user.id)
    )
    if not member.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    chat_res = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = chat_res.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Users in chat
    users_res = await db.execute(
        select(User).join(ChatUser, ChatUser.user_id == User.id).where(ChatUser.chat_id == chat_id)
    )
    users = [UserPublic.model_validate(u) for u in users_res.scalars().all()]

    # Messages (newest first)
    total_res = await db.execute(select(func.count()).select_from(Message).where(Message.chat_id == chat_id))
    total = int(total_res.scalar() or 0)

    msgs_res = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.created_at)).offset(offset).limit(limit)
    )
    messages = [MessageOut.model_validate(m) for m in msgs_res.scalars().all()]

    # Compute display name/avatar for direct chats
    name = chat.name
    avatar = chat.avatar
    if not chat.is_group:
        members_res = await db.execute(
            select(User).join(ChatUser, ChatUser.user_id == User.id).where(ChatUser.chat_id == chat_id)
        )
        members = members_res.scalars().all()
        name, avatar = _other_user_name(members, current_user.id)

    return ChatWithMessagesPage(
        chat=ChatDetail(id=chat.id, is_group=chat.is_group, name=name, avatar=avatar, users=users),
        messages=messages,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message (REST)",
    description="Send a text or image message to a chat; primarily for fallback to WS.",
)
async def send_message_rest(
    chat_id: uuid.UUID,
    payload: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MessageOut:
    is_member = await db.execute(
        select(ChatUser).where(ChatUser.chat_id == chat_id, ChatUser.user_id == current_user.id)
    )
    if not is_member.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chat not found")

    if not payload.text_content and not payload.image_content:
        raise HTTPException(status_code=400, detail="text_content or image_content is required")

    msg = Message(chat_id=chat_id, from_user_id=current_user.id, text_content=payload.text_content, image_content=payload.image_content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return MessageOut.model_validate(msg)


