from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Request,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_async_db
from app.utils import get_user_from_web_token
from typing import Dict
from app.schemas import ChatValid
from pydantic import ValidationError
from app.models import Chat, User

router = APIRouter(prefix="/chat", tags=["CHAT"])

active_users: Dict[str, WebSocket] = {}


@router.websocket("/{token}")
async def websocket_endpoint(
    websocket: WebSocket, token: str,username:str, db: AsyncSession = Depends(get_async_db)
):
    await websocket.accept()
    try:
        db_user = await get_user_from_web_token(token=token, database=db)
        result = await db.execute(select(User).filter(User.username == message.receiver))
        db_receiver = result.scalar_one_or_none()
        if not db_receiver:
            raise HTTPException(status_code=404, detail='user not found')
        active_users[db_user.username] = websocket
        print(active_users)
    except HTTPException as e:
        await websocket.send_text(f"Error: {e.detail}")
        await websocket.close()
        return
    stmt = select(Chat).filter(
        ((Chat.sender_id == db_user.id) & (Chat.receiver_id == db_receiver.id)) |
        ((Chat.sender_id == db_receiver.id) & (Chat.receiver_id == db_user))
    ).order_by(Chat.timestamp)
    result = await db.execute(stmt)
    messages = result.scalar().all()
    websocket.send_json(messages)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            try:
                message = ChatValid(**data)
            except ValidationError:
                await websocket.send_json({"message": "wrong data"})
                continue
            receiver = active_users.get(message.receiver)
            result = await db.execute(select(User).filter(User.username == message.receiver))
            db_receiver = result.scalar_one_or_none()
            if not db_receiver:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
            new_message = Chat(
                message = message.text,
                sender_id = db_user.id,
                receiver_id = db_receiver.id
            )
            db.add(new_message)
            await db.commit()
            if receiver:
                await receiver.send_json(
                    {"sender": message.sender, "text": message.text}
                )
    except WebSocketDisconnect:
        del active_users[db_user.username]
        print(f"Client {db_user.username} disconnected")
    except HTTPException as e:
        await websocket.send_text(f"Error:{e.detail}")
        await websocket.close()
        del active_users[db_user.username]
