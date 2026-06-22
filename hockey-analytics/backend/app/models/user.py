from sqlalchemy import Column, String, Enum, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, enum
from app.database import Base

class UserRole(str, enum.Enum):
    COACH = "coach"
    PARENT = "parent"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PARENT)
    team_id = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    purchases = relationship("Purchase", back_populates="user")
    clip_tags = relationship("ClipTag", back_populates="user")
