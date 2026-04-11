from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.db.init_db import init_db
from app.websocket.manager import manager

settings.media_root_path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.media_root_path.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)
app.mount("/media", StaticFiles(directory=settings.media_root_path), name="media")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "project": settings.project_name,
        "status": "ok",
        "docs": "/docs",
    }


@app.websocket("/ws/queue")
async def queue_websocket(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_json({"event": "heartbeat"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
