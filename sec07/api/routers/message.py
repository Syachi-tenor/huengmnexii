from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends
from sqlmodel import Session, select

from api.db import get_session
from api.schemas.system import Response
from api.schemas.user import User
from api.schemas.message import Message, MessagePost
from .user import get_current_active_user

router = APIRouter()


def get_current_id(session: Session) -> int:
    last = session.exec(
        select(Message).order_by(Message.id.desc()).limit(1)
    ).first()
    if last is None or last.id is None:
        return 0
    return last.id


@router.get("/messages", response_model=Response)
async def get_messages(session: Session = Depends(get_session),
                       current_user: User = Depends(get_current_active_user),
                       from_id: int | None = 1, to_id: int | None = None,
                       from_time: datetime | None = None,
                       important: bool | None = None,
                       ids_only: bool = False):
    """全ての message を返す"""
    if from_id is None or from_id < 1:
        from_id = 1
    if to_id is None:
        # to_id が指定されない場合は，現在の最大IDまで取得する．
        to_id = get_current_id(session)

    query = select(Message).where(Message.id >= from_id)
    query = query.where(Message.id <= to_id)
    if from_time is not None:
        query = query.where(Message.update_time >= from_time)
    if important is not None:
        query = query.where(Message.important == important)
    query = query.order_by(Message.id)

    messages = list(session.exec(query).all())
    ids = [m.id for m in messages if m.id is not None]

    # ID のリストのみ返す
    if ids_only:
        return Response(
            current_id=get_current_id(session),
            current_time=datetime.now(),
            ids=ids)

    message_dict = {m.id: m for m in messages if m.id is not None}
    return Response(
        current_id=get_current_id(session),
        current_time=datetime.now(),
        messages=message_dict)


@router.get("/messages/current_id")
async def get_messages_current_id(session: Session = Depends(get_session),
                                  current_user: User = Depends(get_current_active_user)):
    return {"current_id": get_current_id(session)}


@router.post("/messages", response_model=Message)
async def post_message(message: MessagePost,
                       session: Session = Depends(get_session),
                       current_user: User = Depends(get_current_active_user)):
    """message のPOST"""
    now = datetime.now()
    m = Message(
        name=current_user.username,
        time=now,
        update_time=now,
        **message.model_dump(),
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


@router.get("/messages/{message_id}", response_model=Message)
async def get_message(message_id: int,
                      session: Session = Depends(get_session),
                      current_user: User = Depends(get_current_active_user)):
    """個別 message のGET"""
    m = session.get(Message, message_id)
    # 該当 ID の message が存在しない場合は 404 を返す(他の関数でも同様)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return m


@router.put("/messages/{message_id}", response_model=Message)
async def put_message(message_id: int, message: MessagePost,
                      session: Session = Depends(get_session),
                      current_user: User = Depends(get_current_active_user)):
    """message のPUT"""
    m = session.get(Message, message_id)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m.message = message.message
    m.important = message.important
    m.update_time = datetime.now()
    session.add(m)
    session.commit()
    session.refresh(m)
    return m


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int,
                         session: Session = Depends(get_session),
                         current_user: User = Depends(get_current_active_user)):
    """message のDELETE"""
    m = session.get(Message, message_id)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    session.delete(m)
    session.commit()
    return {"success": True}


@router.get("/messages/{message_id}/important")
async def get_message_important(message_id: int,
                                session: Session = Depends(get_session),
                                current_user: User = Depends(get_current_active_user)):
    """message important flag の GET """
    m = session.get(Message, message_id)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return {"important": m.important}


@router.put("/messages/{message_id}/important")
async def put_message_important(message_id: int,
                                session: Session = Depends(get_session),
                                current_user: User = Depends(get_current_active_user)):
    """message important flag の PUT (important = True)"""
    m = session.get(Message, message_id)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m.update_time = datetime.now()
    m.important = True
    session.add(m)
    session.commit()
    return {"success": True}


@router.delete("/messages/{message_id}/important")
async def delete_message_important(message_id: int,
                                   session: Session = Depends(get_session),
                                   current_user: User = Depends(get_current_active_user)):
    """message important flag の DELETE (important = False)"""
    m = session.get(Message, message_id)
    if m is None:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m.update_time = datetime.now()
    m.important = False
    session.add(m)
    session.commit()
    return {"success": True}
