from sqlmodel import SQLModel, Field


class User(SQLModel):
    username: str = Field(primary_key=True)


class UserInDB(User, table=True):
    hashed_password: str


class UserCreate(User):
    password: str
