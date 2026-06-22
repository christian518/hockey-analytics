from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid, os, aiofiles, httpx
from app.database import get_db
from app.models.game import Game, GameStatus, VideoSourceType
from app.models.user import User
from app.core.security import get_current_user, get_current_coach, get_optional_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

class CreateGameRequest(BaseModel):
    name: str
    home_team: str
    away_team: str
    tournament_id: Optional[str] = None
    video_source_type: VideoSourceType
    video_source_url: Optional[str] = None
    is_public: bool = False

class GameResponse(BaseModel):
    id: str
    name: str
    home_team: str
    away_team: str
    status: str
    video_source_type: str
    home_score: int
    away_score: int
    total_shots: int
    is_public: bool
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    thumbnail_url: Optional[str]

def _to_response(game):
    return GameResponse(id=str(game.id), name=game.name, home_team=game.home_team, away_team=game.away_team, status=game.status.value, video_source_type=game.video_source_type.value, home_score=game.home_score, away_score=game.away_score, total_shots=game.total_shots, is_public=game.is_public, started_at=game.started_at, ended_at=game.ended_at, created_at=game.created_at, thumbnail_url=game.thumbnail_url)

@router.post("", response_model=GameResponse)
async def create_game(data: CreateGameRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_coach)):
    game = Game(id=uuid.uuid4(), name=data.name, home_team=data.home_team, away_team=data.away_team, tournament_id=data.tournament_id, video_source_type=data.video_source_type, video_source_url=data.video_source_url, is_public=data.is_public)
    db.add(game)
    await db.commit()
    await db.refresh(game)
    return _to_response(game)

@router.post("/{game_id}/upload-video")
async def upload_video(game_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...), db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_coach)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    os.makedirs(settings.VIDEO_STORAGE_PATH, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    path = os.path.join(settings.VIDEO_STORAGE_PATH, f"game_{game_id}{ext}")
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    game.video_file_path = path
    game.status = GameStatus.PROCESSING
    await db.commit()
    return {"message": "Uploaded", "file_path": path}

@router.post("/{game_id}/start")
async def start_game(game_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_coach)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game.status = GameStatus.LIVE
    game.started_at = datetime.utcnow()
    await db.commit()
    return {"message": "Game started"}

@router.post("/{game_id}/stop")
async def stop_game(game_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_coach)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game.status = GameStatus.COMPLETED
    game.ended_at = datetime.utcnow()
    await db.commit()
    return {"message": "Game stopped"}

@router.get("", response_model=List[GameResponse])
async def list_games(db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    query = select(Game).order_by(desc(Game.created_at)).limit(50)
    if not current_user or current_user.role.value == "parent":
        query = query.where(Game.is_public == True)
    result = await db.execute(query)
    return [_to_response(g) for g in result.scalars().all()]

@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return _to_response(game)

@router.get("/{game_id}/summary")
async def get_summary(game_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    from app.models.event import Event
    from app.models.clip import Clip
    counts_result = await db.execute(select(Event.event_type, func.count(Event.id)).where(Event.game_id == game_id).group_by(Event.event_type))
    event_counts = {r[0].value: r[1] for r in counts_result}
    clips_result = await db.execute(select(func.count(Clip.id)).where(Clip.game_id == game_id))
    comp_result = await db.execute(select(Clip).where(Clip.game_id == game_id, Clip.clip_type == "compilation"))
    comp = comp_result.scalar_one_or_none()
    return {"game_id": str(game_id), "name": game.name, "home_team": game.home_team, "away_team": game.away_team, "home_score": game.home_score, "away_score": game.away_score, "total_shots": game.total_shots, "event_counts": event_counts, "total_highlights": clips_result.scalar(), "compilation_url": comp.clip_url if comp else None, "status": game.status.value}