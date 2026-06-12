from sqlalchemy import Column, String, Enum, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from app.database import Base

class EventType(str, enum.Enum):
    SHOT = "shot"
    GOAL = "goal"
    PRESSURE = "pressure"
    SAVE = "save"

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_id = Column(UUID(as_uuid=True), ForeignKey("games.id"), nullable=False, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    timestamp = Column(Float, nullable=False)
    game_clock = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    clip_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    game = relationship("Game", back_populates="events")
    clip = relationship("Clip", back_populates="event", uselist=False)
