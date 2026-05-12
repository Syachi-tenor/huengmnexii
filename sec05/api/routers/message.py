from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends

from api.db import get_system
from api.schemas.system import System, Response
from api.schemas.message import Message, MessageBase

router = APIRouter()


@router.get("/messages", response_model=Response)
async def get_messages(system: System = Depends(get_system),
                       from_id: int | None = 1, to_id: int | None = None,
                       from_time: datetime | None = None,
                       important: bool | None = None,
                       ids_only: bool = False):
    """全ての message を返す"""
    if from_id is None or from_id < 1:
        from_id = 1
    if to_id is None:
        # to_id が指定されない場合は，現在の最大IDまで取得する．
        to_id = system.current_id
    l: list = []
    for i in range(from_id, to_id + 1):
        if i in system.messages:
            if from_time is None or \
               from_time <= system.messages[i].update_time:
                if important is None:
                    l.append(i)
                elif system.messages[i].important == important:
                    l.append(i)

    # ID のリストのみ返す
    if ids_only:
        return Response(
            current_id=system.current_id,
            current_time=datetime.now(),
            ids=l)

    return Response(
        current_id=system.current_id,
        current_time=datetime.now(),
        messages={i: system.messages[i] for i in l})


@router.get("/messages/current_id")
async def get_messages_current_id(system: System = Depends(get_system)):
    return {"current_id": system.current_id}


@router.post("/messages", response_model=Message)
async def post_message(message: MessageBase,
                       system: System = Depends(get_system)):
    """message のPOST"""
    next_id = system.current_id + 1
    now = datetime.now()
    m = Message(
        id=next_id,
        time=now,
        update_time=now,
        **message.model_dump(),
    )
    system.messages[next_id] = m
    system.current_id = next_id
    return m


@router.get("/messages/{message_id}", response_model=Message)
async def get_message(message_id: int,
                      system: System = Depends(get_system), ):
    """個別 message のGET"""
    # 該当 ID の message が存在しない場合は 404 を返す(他の関数でも同様)
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return system.messages[message_id]


@router.put("/messages/{message_id}", response_model=Message)
async def put_message(message_id: int,
                      message: MessageBase,
                      system: System = Depends(get_system)):
    """message のPUT"""
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m = system.messages[message_id]
    m.message = message.message
    m.important = message.important
    m.update_time = datetime.now()
    system.messages[message_id] = m
    return m


@router.delete("/messages/{message_id}")
async def delete_message(message_id: int,
                         system: System = Depends(get_system)):
    """message のDELETE"""
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    del system.messages[message_id]
    return {"success": True}


@router.get("/messages/{message_id}/important")
async def get_message_important(message_id: int,
                                system: System = Depends(get_system)):
    """message important flag の GET """
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    return {"important": system.messages[message_id].important}


@router.put("/messages/{message_id}/important")
async def put_message_important(message_id: int,
                                system: System = Depends(get_system)):
    """message important flag の PUT (important = True)"""
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m = system.messages[message_id]
    m.update_time = datetime.now()
    m.important = True
    return {"success": True}


@router.delete("/messages/{message_id}/important")
async def delete_message_important(message_id: int,
                                   system: System = Depends(get_system)):
    """message important flag の DELETE (important = False)"""
    if message_id not in system.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")

    m = system.messages[message_id]
    m.update_time = datetime.now()
    m.important = False
    return {"success": True}
