from sqlalchemy import Column, String, Enum, DateTime, Boolean, Integer, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from app.database import Base

class GameStatus(str, enum.Enum):
    PENDING = "pending"
    LIVE = "live"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

class VideoSourceType(str, enum.Enum):
    RTSP = "rtsp"
    FILE = "file"
    WEBCAM = "webcam"

class Game(Base):
    __tablename__ = "games"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tournament_id = Column(String(100), nullable=True)
    name = Column(String(255), nullable=False)
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    status = Column(Enum(GameStatus), default=GameStatus.PENDING, index=True)
    video_source_type = Column(Enum(VideoSourceType), nullable=False)
    video_source_url = Column(Text, nullable=True)
    video_file_path = Column(Text, nullable=True)
    recording_path = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    total_shots = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    events = relationship("Event", back_populates="game", order_by="Event.timestamp")
    clips = relationship("Clip", back_populates="game")
    purchases = relationship("Purchase", back_populates="game")
