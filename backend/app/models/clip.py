from sqlalchemy import Column, String, Enum, DateTime, Float, Integer, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from app.database import Base

class ClipType(str, enum.Enum):
    EVENT = "event"
    COMPILATION = "compilation"
    FAVORITE = "favorite"

class Clip(Base):
    __tablename__ = "clips"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True, unique=True)
    clip_type = Column(Enum(ClipType), default=ClipType.EVENT)
    title = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False)
    clip_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    file_size = Column(Integer, nullable=True)
    is_free = Column(Boolean, default=False)
    rank_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    game = relationship("Game", back_populates="clips")
    event = relationship("Event", back_populates="clip")
    tags = relationship("ClipTag", back_populates="clip")

class ClipTag(Base):
    __tablename__ = "clip_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clip_id = Column(UUID(as_uuid=True), ForeignKey("clips.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tag = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    clip = relationship("Clip", back_populates="tags")
    user = relationship("User", back_populates="clip_tags")
