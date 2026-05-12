from datetime import datetime
from pydantic import BaseModel, Field


class MessagePost(BaseModel):
    message: str | None = Field(None,
                                examples=["Default Message"],
                                description="Message body")
    important: bool = Field(False, description="Important or not")


class MessageBase(MessagePost):
    name: str | None = Field(None,
                             examples=["System"],
                             description="Message from")


class Message(MessageBase):
    id: int | None = Field(None, description="Message ID")
    time: datetime | None = Field(None, description="Message post time")
    update_time: datetime | None = Field(None,
                                         description="Message update time")
