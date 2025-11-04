import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Set

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.chat import ChatUser
from app.models.message import Message, MessageSeen
from app.schemas.message import MessageCreate, MessageOut


router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ChatConnectionManager:
    def __init__(self) -> None:
        self.chat_connections: dict[uuid.UUID, set[WebSocket]] = {}

    async def connect(self, chat_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.chat_connections.setdefault(chat_id, set()).add(websocket)

    def disconnect(self, chat_id: uuid.UUID, websocket: WebSocket) -> None:
        conns = self.chat_connections.get(chat_id)
        if conns and websocket in conns:
            conns.remove(websocket)
            if not conns:
                self.chat_connections.pop(chat_id, None)

    async def broadcast(self, chat_id: uuid.UUID, message: dict[str, Any]) -> None:
        data = json.dumps(message, default=str)
        for ws in list(self.chat_connections.get(chat_id, set())):
            try:
                await ws.send_text(data)
            except Exception:
                # Drop broken connections silently
                self.disconnect(chat_id, ws)


manager = ChatConnectionManager()


async def _authenticate_ws(websocket: WebSocket) -> dict[str, Any]:
    token = websocket.query_params.get("token")
    if not token:
        # Try Authorization header "Bearer <token>"
        auth = websocket.headers.get("authorization") or websocket.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(" ", 1)[1]
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        return decode_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise


@router.websocket("/chats/{chat_id}")
async def ws_chat(
    websocket: WebSocket,
    chat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    payload = await _authenticate_ws(websocket)
    user_sub = payload.get("sub")
    try:
        user_id = uuid.UUID(user_sub)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Ensure membership
    member = await db.execute(select(ChatUser).where(ChatUser.chat_id == chat_id, ChatUser.user_id == user_id))
    if not member.scalar_one_or_none():
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(chat_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
            except Exception:
                await websocket.send_text(json.dumps({"type": "error", "error": "Invalid JSON"}))
                continue

            event_type = data.get("type")
            if event_type == "message":
                msg_in = MessageCreate(**{k: data.get(k) for k in ("text_content", "image_content")})
                if not msg_in.text_content and not msg_in.image_content:
                    await websocket.send_text(json.dumps({"type": "error", "error": "text_content or image_content required"}))
                    continue
                msg = Message(chat_id=chat_id, from_user_id=user_id, text_content=msg_in.text_content, image_content=msg_in.image_content)
                db.add(msg)
                await db.commit()
                await db.refresh(msg)
                out = MessageOut.model_validate(msg)
                await manager.broadcast(chat_id, {"type": "message", "message": out.model_dump(mode="json")})
            elif event_type == "seen":
                ids = data.get("message_ids") or []
                for mid in ids:
                    try:
                        m_uuid = uuid.UUID(str(mid))
                    except Exception:
                        continue
                    db.add(MessageSeen(message_id=m_uuid, user_id=user_id))
                try:
                    await db.commit()
                except Exception:
                    # Unique constraint violations are okay (already seen)
                    await db.rollback()
                await manager.broadcast(chat_id, {"type": "seen", "user_id": str(user_id), "message_ids": [str(i) for i in ids]})
            elif event_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                await websocket.send_text(json.dumps({"type": "error", "error": "Unknown event type"}))
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)


