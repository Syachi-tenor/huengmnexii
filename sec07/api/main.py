from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from api.routers import message, user
from api.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['null'],
    allow_methods=['*'],
)


@app.get("/", response_class=HTMLResponse)
async def get_client():
    """Return client HTML"""
    data = ''
    with open('client.html', 'rt', encoding='utf-8') as f:
        data = f.read()
    return data


@app.get("/main.js", response_class=FileResponse)
async def get_main_js():
    return FileResponse("main.js", media_type="text/javascript")


app.include_router(message.router)
app.include_router(user.router)
