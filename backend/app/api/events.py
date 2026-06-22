from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid, json
from app.database import get_db
from app.models.event import Event, EventType
from app.core.websocket_manager import manager

router = APIRouter()

class EventResponse(BaseModel):
    id: str
    game_id: str
    event_type: str
    timestamp: float
    game_clock: Optional[str]
    confidence: float
    clip_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime

class CreateEventRequest(BaseModel):
    game_id: str
    event_type: str
    timestamp: float
    game_clock: Optional[str] = None
    confidence: float
    metadata: Optional[dict] = None

@router.post("", response_model=EventResponse)
async def create_event(data: CreateEventRequest, db: AsyncSession = Depends(get_db)):
    event = Event(id=uuid.uuid4(), game_id=data.game_id, event_type=EventType(data.event_type), timestamp=data.timestamp, game_clock=data.game_clock, confidence=data.confidence, metadata_json=json.dumps(data.metadata) if data.metadata else None)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    from app.models.game import Game
    game_result = await db.execute(select(Game).where(Game.id == data.game_id))
    game = game_result.scalar_one_or_none()
    if game:
        source = game.video_source_url or game.video_file_path
        if source:
            from app.workers.clip_tasks import generate_clip
            generate_clip.delay(str(data.game_id), str(event.id), data.event_type, source, data.timestamp)
    await manager.broadcast_alert(str(data.game_id), {"event_id": str(event.id), "event_type": data.event_type, "timestamp": data.timestamp, "game_clock": data.game_clock, "confidence": data.confidence})
    return EventResponse(id=str(event.id), game_id=str(event.game_id), event_type=event.event_type.value, timestamp=event.timestamp, game_clock=event.game_clock, confidence=event.confidence, clip_url=event.clip_url, thumbnail_url=event.thumbnail_url, created_at=event.created_at)

@router.get("/game/{game_id}", response_model=List[EventResponse])
async def get_game_events(game_id: str, event_type: Optional[str] = Query(None), limit: int = Query(50, le=200), db: AsyncSession = Depends(get_db)):
    query = select(Event).where(Event.game_id == game_id).order_by(desc(Event.timestamp)).limit(limit)
    if event_type:
        query = query.where(Event.event_type == EventType(event_type))
    result = await db.execute(query)
    return [EventResponse(id=str(e.id), game_id=str(e.game_id), event_type=e.event_type.value, timestamp=e.timestamp, game_clock=e.game_clock, confidence=e.confidence, clip_url=e.clip_url, thumbnail_url=e.thumbnail_url, created_at=e.created_at) for e in result.scalars().all()]