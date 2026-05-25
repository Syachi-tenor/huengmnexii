# Based on the following page's code.
# https://fastapi.tiangolo.com/ja/tutorial/security/oauth2-jwt/

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

import jwt
from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash

from api.schemas.system import System
from api.schemas.user import User, UserInDB, UserCreate
from api.schemas.token import Token, TokenData
from api.db import get_system

SECRET_KEY = "410f0f0770a1a93c9d3010b6276490d757f0351ec6365fa4f4660a5006b7d269"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        return db[username]
    return None


def authenticate_user(user_db, username: str, password: str):
    user = get_user(user_db, username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        system: System = Depends(get_system)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(system.users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    system: System = Depends(get_system)
) -> Token:
    user = authenticate_user(system.users_db,
                             form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/users")
async def create_user(user: UserCreate, system: System = Depends(get_system)):
    username = user.username.strip()
    password = user.password.strip()

    if username in system.users_db:
        return "Already exists"
    if len(password) == 0:
        return "Empty password"
    if len(username) == 0:
        return "Empty username"

    system.users_db[username] = UserInDB(
        username=username,
        hashed_password=password_hash.hash(password))
    return "Success"


@router.get("/users/me/")
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user
