from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

import api.schemas.message as message_schema

router = APIRouter()


@router.get("/messages", response_model=message_schema.Messages)
async def get_messages(request: Request):
    """全ての message を返す"""
    return request.app.state.messages

@router.get("/messages/important", response_model=message_schema.Messages)
async def get_messages(request: Request):
    """全ての message を返す"""
    important_messages = []
    for message in request.app.state.messages.messages:
        if (message.important == True):
            important_messages.apeend
    return important_messages

@router.post("/messages", response_model=message_schema.Message)
async def post_message(request: Request, message: message_schema.MessageBase):
    """message のPOST"""
    m = message_schema.Message(time=datetime.now(),
                               id=request.app.state.counter,
                               **message.model_dump())
    request.app.state.messages.messages[request.app.state.counter] = m
    request.app.state.counter += 1
    return m


@router.get("/messages/{message_id}", response_model=message_schema.Message)
async def get_message(request: Request, message_id: int):
    """個別 message のGET"""
    # 該当 ID の message が存在しない場合は 404 を返す(他の関数でも同様)
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    return request.app.state.messages.messages[message_id]


@router.put("/messages/{message_id}", response_model=message_schema.Message)
async def put_message(request: Request,
                      message_id: int, message: message_schema.MessageBase):
    """message のPUT"""
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    m = message_schema.Message(time=datetime.now(), id=message_id,
                               **message.model_dump())
    request.app.state.messages.messages[message_id] = m
    return m


@router.delete("/messages/{message_id}")
async def delete_message(request: Request, message_id: int):
    """message のDELETE"""
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    del request.app.state.messages.messages[message_id]
    return {"success": True}


@router.get("/messages/{message_id}/important")
async def get_message_important(request: Request, message_id: int):
    """message important flag の GET """
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    # get_message_important
    important = request.app.state.messages.messages[message_id].important
    return {"important": important}


@router.put("/messages/{message_id}/important")
async def put_message_important(request: Request, message_id: int):
    """message important flag の PUT (important = True)"""
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    # put_message_important
    request.app.state.messages.messages[message_id].important = True
    return {"success": True}


@router.delete("/messages/{message_id}/important")
async def delete_message_important(request: Request, message_id: int):
    """message important flag の DELETE (important = False)"""
    if message_id not in request.app.state.messages.messages:
        raise HTTPException(status_code=404,
                            detail="Message cannot be found")
    # delete_message_important
    request.app.state.messages.messages[message_id].important = False
    return {"success": True}
