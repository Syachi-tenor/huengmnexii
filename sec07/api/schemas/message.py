from datetime import datetime
from sqlmodel import Field, SQLModel


class MessagePost(SQLModel):
    message: str | None = Field(None,
                                description="Message body")
    important: bool = Field(False, description="Important or not")


class MessageBase(MessagePost):
    name: str | None = Field(None,
                             description="Message from")


class Message(MessageBase, table=True):
    id: int | None = Field(None, primary_key=True,
                           description="Message ID")
    time: datetime | None = Field(None, description="Message post time")
    update_time: datetime | None = Field(None,
                                         description="Message update time")
