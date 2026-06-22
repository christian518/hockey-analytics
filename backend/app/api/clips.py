from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.clip import Clip, ClipTag
from app.models.purchase import Purchase, PurchaseStatus
from app.models.user import User
from app.core.security import get_current_user, get_optional_user
from app.config import get_settings
import uuid

router = APIRouter()
settings = get_settings()

class ClipResponse(BaseModel):
    id: str
    game_id: str
    clip_type: str
    title: str
    clip_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[float]
    is_free: bool
    is_locked: bool
    rank_score: float
    created_at: datetime

@router.get("/game/{game_id}", response_model=List[ClipResponse])
async def get_game_clips(game_id: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    result = await db.execute(select(Clip).where(Clip.game_id == game_id).order_by(desc(Clip.rank_score), desc(Clip.created_at)))
    clips = result.scalars().all()
    has_access = False
    if current_user and current_user.role.value in ["coach", "admin"]:
        has_access = True
    response = []
    free_count = 0
    for clip in clips:
        is_free = clip.is_free or free_count < settings.FREE_CLIP_LIMIT
        can_access = has_access or is_free
        free_count += 1
        response.append(ClipResponse(id=str(clip.id), game_id=str(clip.game_id), clip_type=clip.clip_type.value, title=clip.title, clip_url=clip.clip_url if can_access else None, thumbnail_url=clip.thumbnail_url, duration=clip.duration, is_free=is_free, is_locked=not can_access, rank_score=clip.rank_score, created_at=clip.created_at))
    return response

@router.post("/{clip_id}/tag")
async def tag_clip(clip_id: str, tag: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    if tag not in {"good_play", "needs_work", "favorite"}:
        raise HTTPException(status_code=400, detail="Invalid tag")
    result = await db.execute(select(Clip).where(Clip.id == clip_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Clip not found")
    db.add(ClipTag(id=uuid.uuid4(), clip_id=clip_id, user_id=current_user.id, tag=tag))
    await db.commit()
    return {"message": "Tag added", "tag": tag}