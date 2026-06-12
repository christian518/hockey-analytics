from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import logging
from app.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hockey Analytics API")
    await init_db()
    yield
    logger.info("Shutting down")

app = FastAPI(title="Hockey Analytics API", version="1.0.0", lifespan=lifespan)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from app.api.auth import router as auth_router
from app.api.games import router as games_router
from app.api.events import router as events_router
from app.api.clips import router as clips_router
from app.api.payments import router as payments_router
from app.api.websocket import router as ws_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(games_router, prefix="/api/v1/games", tags=["games"])
app.include_router(events_router, prefix="/api/v1/events", tags=["events"])
app.include_router(clips_router, prefix="/api/v1/clips", tags=["clips"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(ws_router, prefix="/api/v1/ws", tags=["websocket"])

@app.get("/health")
async def health():
    return {"status": "ok", "service": "hockey-analytics-api"}
